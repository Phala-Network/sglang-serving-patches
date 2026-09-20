#!/usr/bin/env python3
"""Verify source-derived GLM profiles. JSON syntax is a supported YAML subset."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


class VerificationError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def git(repo, *args, env=None):
    result = subprocess.run(
        ["git", "-c", "core.autocrlf=false", "-C", str(repo), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    if result.returncode:
        raise VerificationError(f"git {' '.join(args)}: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def oid(value, label):
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value), f"{label}: expected full Git SHA-1")
    return value


def relative_file(root, value):
    require(isinstance(value, str), "file path must be a string")
    path = Path(value)
    require(not path.is_absolute() and ".." not in path.parts, f"unsafe relative path: {value}")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()) and resolved.is_file(), f"missing or escaped file: {value}")
    return resolved


def load_profile(path):
    raw = path.read_bytes()
    profile = json.loads(raw)
    require(profile.get("schema_version") == 1, "unsupported schema_version")
    require(profile.get("governor") == {"enabled": False}, "this verifier supports Governor-disabled profiles only")
    require(isinstance(profile.get("patches"), list) and profile["patches"], "empty patch selection")
    return profile, hashlib.sha256(raw).hexdigest()


def verify(source, root, path, run_tests=True):
    profile, profile_hash = load_profile(path)
    baseline = oid(profile["upstream"]["commit"], "upstream.commit")
    require(git(source, "rev-parse", f"{baseline}^{{commit}}").decode().strip() == baseline, "upstream commit mismatch")
    expected = oid(profile["expected_tree"], "expected_tree")
    if profile.get("engine_commit"):
        engine = oid(profile["engine_commit"], "engine_commit")
        require(git(source, "rev-parse", f"{engine}^{{tree}}").decode().strip() == expected, "engine_commit does not identify expected_tree")
    selected = set()
    patch_results = []
    for entry in profile["patches"]:
        patch_id = entry["id"]
        require(isinstance(patch_id, str) and patch_id and patch_id not in selected, f"duplicate/invalid patch id: {patch_id}")
        dependencies = entry["depends_on"]
        require(isinstance(dependencies, list) and len(set(dependencies)) == len(dependencies), f"{patch_id}: malformed dependencies")
        require(all(dep in selected for dep in dependencies), f"{patch_id}: missing or unordered dependencies: {dependencies}")
        require(entry.get("category") in {"common", "model", "external-overlay"}, f"{patch_id}: invalid category")
        require(isinstance(entry.get("source_pr"), str) and entry["source_pr"].startswith("https://github.com/"), f"{patch_id}: missing source PR")
        commit = oid(entry["source_commit"], f"{patch_id}.source_commit")
        parent = oid(entry["source_parent"], f"{patch_id}.source_parent")
        parents = git(source, "show", "-s", "--format=%P", commit).decode().strip().split()
        require(parents == [parent], f"{patch_id}: expected exact single source parent {parent}, got {parents}")
        require(git(source, "rev-parse", f"{parent}^{{commit}}").decode().strip() == parent, f"{patch_id}: invalid parent")
        patch = relative_file(root, entry["path"])
        data = patch.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        require(sha == entry["sha256"], f"{patch_id}: patch SHA-256 mismatch")
        exported = git(source, "diff", "--binary", "--full-index", "--no-ext-diff", "--no-textconv", parent, commit)
        require(data == exported, f"{patch_id}: patch bytes differ from deterministic source export")
        if entry["category"] == "external-overlay":
            provenance = entry.get("external_provenance", {})
            require(provenance.get("repository") and provenance.get("path"), f"{patch_id}: external provenance missing repository/path")
            require(provenance.get("commit") or (provenance.get("version") and re.fullmatch(r"[0-9a-f]{64}", provenance.get("before_sha256", ""))), f"{patch_id}: external provenance needs commit or version/before_sha256")
        selected.add(patch_id)
        patch_results.append({"id": patch_id, "sha256": sha, "source_commit": commit, "source_parent": parent})

    # A separate object database/index and checkout avoid modifying the source repo.
    with tempfile.TemporaryDirectory(prefix="glm-profile-") as temporary:
        materialized = Path(temporary)
        git(materialized, "init", "--quiet")
        source_objects = git(source, "rev-parse", "--git-path", "objects").decode().strip()
        objects = Path(source_objects)
        if not objects.is_absolute():
            objects = (source / objects).resolve()
        env = os.environ.copy()
        env["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = str(objects)
        git(materialized, "read-tree", baseline, env=env)
        git(materialized, "checkout-index", "--all", "--index", env=env)
        for entry in profile["patches"]:
            git(materialized, "apply", "--index", "--whitespace=nowarn", str(relative_file(root, entry["path"])), env=env)
        actual = git(materialized, "write-tree", env=env).decode().strip()
        require(actual == expected, f"complete tree mismatch: expected {expected}, got {actual}")
        runtime_tree = git(materialized, "rev-parse", f"{actual}:python/sglang", env=env).decode().strip()
        if profile.get("deployed_python_tree"):
            require(runtime_tree == oid(profile["deployed_python_tree"], "deployed_python_tree"), f"deployed python/sglang tree mismatch: {runtime_tree}")
        regressions = profile.get("regressions", [])
        require(isinstance(regressions, list) and regressions, "profile must declare affected regression tests")
        test_results = []
        if run_tests:
            for test in regressions:
                script = relative_file(materialized, test["path"])
                args = test.get("args", [])
                require(isinstance(args, list) and all(isinstance(a, str) for a in args), "test args must be strings")
                test_env = env.copy()
                test_env["PYTHONPATH"] = str(materialized / "python")
                test_env["SGLANG_SOURCE_ROOT"] = str(materialized)
                test_env["SGLANG_TEST_SOURCE_ROOT"] = str(materialized / "python/sglang/srt")
                test_env["HICACHE_ACK_TEST_SOURCE_ROOT"] = str(materialized)
                test_env["HICACHE_ACK_TEST_GLOO"] = "0"
                test_env["SGLANG_TEST_RESULT_PATH"] = str(materialized / "test-result.json")
                test_env["PYTHONNOUSERSITE"] = "1"
                test_env.pop("SGLANG_TEST_INSTALLED_ROOT", None)
                overrides = test.get("env", {})
                require(isinstance(overrides, dict) and set(overrides) <= {"FLASHINFER_ALLREDUCE_SOURCE"}, "unsupported regression environment override")
                for key, value in overrides.items():
                    test_env[key] = str(relative_file(materialized, value))
                command = [sys.executable, str(script), *args]
                completed = subprocess.run(command, cwd=materialized, env=test_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                print(completed.stdout, file=sys.stderr, end="")
                require(completed.returncode == 0, f"regression failed: {test['path']}")
                require(not re.search(r"Ran 0 tests\b", completed.stdout), f"regression executed zero tests: {test['path']}")
                test_results.append({"path": test["path"], "args": args, "env": overrides, "exit_code": completed.returncode})
        return {"profile": str(path.relative_to(root)), "profile_sha256": profile_hash,
                "upstream_commit": baseline, "complete_tree": actual, "python_tree": runtime_tree,
                "patches": patch_results, "regressions": test_results, "tests_executed": run_tests}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-repo", type=Path)
    parser.add_argument("--profile", action="append", type=Path)
    parser.add_argument("--self-test", action="store_true", help="exercise real Git positive and tampering cases")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.source_repo or not args.profile:
        parser.error("--source-repo and --profile are required unless --self-test is used")
    root = Path(__file__).resolve().parents[1]
    try:
        results = [verify(args.source_repo.resolve(), root, path.resolve()) for path in args.profile]
    except (VerificationError, KeyError, ValueError, OSError, TypeError) as error:
        print(f"verification failed: {error}", file=sys.stderr)
        return 1
    result = json.dumps({"schema_version": 1, "profiles": results}, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8", newline="\n")
    print(result, end="")
    return 0


def self_test():
    with tempfile.TemporaryDirectory(prefix="glm-verifier-test-") as directory:
        root = Path(directory)
        source = root / "source"
        source.mkdir()
        git(source, "init", "--quiet")
        git(source, "config", "user.name", "Verifier test")
        git(source, "config", "user.email", "verifier@example.invalid")
        (source / "python/sglang").mkdir(parents=True)
        (source / "python/sglang/value.py").write_text("VALUE = 1\n", encoding="utf-8")
        git(source, "add", ".")
        git(source, "commit", "--quiet", "-m", "base")
        base = git(source, "rev-parse", "HEAD").decode().strip()
        (source / "python/sglang/value.py").write_text("VALUE = 2\n", encoding="utf-8")
        (source / "regression.py").write_text("from pathlib import Path\nassert Path('python/sglang/value.py').read_text() == 'VALUE = 2\\n'\n", encoding="utf-8")
        git(source, "add", ".")
        git(source, "commit", "--quiet", "-m", "fix")
        commit = git(source, "rev-parse", "HEAD").decode().strip()
        patch = git(source, "diff", "--binary", "--full-index", base, commit)
        patch_path = root / "fix.patch"
        patch_path.write_bytes(patch)
        profile = {"schema_version": 1, "upstream": {"commit": base}, "governor": {"enabled": False},
                   "patches": [{"id": "fix", "path": "fix.patch", "sha256": hashlib.sha256(patch).hexdigest(),
                                "source_commit": commit, "source_parent": base, "depends_on": [], "category": "common",
                                "source_pr": "https://github.com/example/source/pull/1"}],
                   "expected_tree": git(source, "rev-parse", "HEAD^{tree}").decode().strip(),
                   "regressions": [{"path": "regression.py", "args": []}]}
        profile_path = root / "profile.yaml"
        def save(value):
            profile_path.write_text(json.dumps(value), encoding="utf-8")
        save(profile)
        verify(source, root, profile_path)
        cases = [
            ("hash", lambda p: p["patches"][0].update(sha256="0" * 64), "SHA-256 mismatch"),
            ("dependency", lambda p: p["patches"][0].update(depends_on=["omitted"]), "missing or unordered"),
            ("tree", lambda p: p.update(expected_tree="0" * 40), "complete tree mismatch"),
            ("parent", lambda p: p["patches"][0].update(source_parent=commit), "exact single source parent"),
        ]
        for name, mutate, expected in cases:
            altered = json.loads(json.dumps(profile))
            mutate(altered)
            save(altered)
            try:
                verify(source, root, profile_path)
            except VerificationError as error:
                require(expected in str(error), f"{name}: unexpected failure: {error}")
            else:
                raise VerificationError(f"{name}: tampering accepted")
        altered = json.loads(json.dumps(profile))
        changed = patch.replace(b"+VALUE = 2", b"+VALUE = 3")
        patch_path.write_bytes(changed)
        altered["patches"][0]["sha256"] = hashlib.sha256(changed).hexdigest()
        save(altered)
        try:
            verify(source, root, profile_path)
        except VerificationError as error:
            require("deterministic source export" in str(error), f"export: unexpected failure: {error}")
        else:
            raise VerificationError("export: edited patch with updated hash accepted")
        print("Verifier self-test passed: real Git positive case and 5 rejection cases")


if __name__ == "__main__":
    sys.exit(main())
