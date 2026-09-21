#!/usr/bin/env python3
"""Export and verify model selectors against immutable Phala SGLang commits."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SELECTORS = ROOT / "selectors.json"
VERIFICATION = ROOT / "selector-verification.json"


def git(repo, *args, env=None, check=True):
    result = subprocess.run(
        ["git", "-c", "core.autocrlf=false", "-C", str(repo), *args],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return result


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def resolve_branch(repo, branch):
    for ref in (f"phala/{branch}", f"origin/{branch}", branch):
        result = git(repo, "rev-parse", "--verify", ref, check=False)
        if result.returncode == 0:
            return ref, result.stdout.decode().strip()
    raise AssertionError(f"missing fork branch: {branch}")


def export_patch(repo, commit):
    parent = git(repo, "rev-parse", commit + "^").stdout.decode().strip()
    data = git(
        repo,
        "diff",
        "--binary",
        "--full-index",
        "--no-ext-diff",
        "--no-renames",
        parent,
        commit,
        "--",
    ).stdout
    return parent, data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    document = json.loads(SELECTORS.read_text(encoding="utf-8"))
    results = {}
    generated = {}
    for name, selector in document["selectors"].items():
        commit = selector["fork_commit"]
        expected_tree = selector["fork_tree"]
        actual_tree = git(args.source, "rev-parse", commit + "^{tree}").stdout.decode().strip()
        assert actual_tree == expected_tree, f"fork tree differs: {name}"
        branch_ref, branch_commit = resolve_branch(args.source, selector["fork_branch"])
        assert branch_commit == commit, f"branch tip differs: {name}: {branch_ref}"

        for patch in selector.get("patches", []):
            target = ROOT / patch["path"]
            if patch.get("source_commit"):
                parent, exported = export_patch(args.source, patch["source_commit"])
                assert sha256(exported) == patch["sha256"], f"fork export differs: {patch['path']}"
                generated[patch["path"]] = exported
                patch["source_parent"] = parent
                if not args.check:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(exported)
            assert target.is_file(), f"missing patch: {patch['path']}"
            actual = target.read_bytes()
            assert sha256(actual) == patch["sha256"], f"patch hash differs: {patch['path']}"

        mode = selector.get("replay_mode", "reference_only")
        result = {
            "passed": True,
            "fork_commit": commit,
            "fork_tree": expected_tree,
            "fork_branch": selector["fork_branch"],
            "resolved_branch_ref": branch_ref,
            "patch_count": len(selector.get("patches", [])),
            "replay_mode": mode,
            "status": selector["status"],
            "validation_boundary": selector.get("validation_boundary", selector.get("required_closure", "")),
        }
        if mode in ("exact", "expected_failure"):
            with tempfile.TemporaryDirectory(prefix="sglang-selector-replay-") as temporary:
                env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / "index"))
                git(args.source, "read-tree", selector["source_parent"], env=env)
                applied = 0
                failure = None
                for patch in selector["patches"]:
                    target = str((ROOT / patch["path"]).resolve())
                    checked = git(args.source, "apply", "--cached", "--check", target, env=env, check=False)
                    if checked.returncode:
                        failure = patch["path"]
                        break
                    git(args.source, "apply", "--cached", target, env=env)
                    applied += 1
                if mode == "exact":
                    assert failure is None, f"selector replay failed: {name}: {failure}"
                    replay_tree = git(args.source, "write-tree", env=env).stdout.decode().strip()
                    assert replay_tree == expected_tree, f"selector replay tree differs: {name}"
                    result["replay_tree"] = replay_tree
                else:
                    assert failure == selector["expected_failure_patch"], f"unexpected failure: {name}: {failure}"
                    assert applied == selector["expected_applied_before_failure"], f"failure count differs: {name}"
                    result["passed"] = False
                    result["applied_before_failure"] = applied
                    result["failed_patch"] = failure

        results[name] = result

    for path, data in generated.items():
        target = ROOT / path
        if args.check:
            assert target.read_bytes() == data, f"generated bytes differ: {path}"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

    verification = {
        "schema": "phala.sglang.selector-verification.v2",
        "as_of": "2026-09-21",
        "source_repository": "https://github.com/Phala-Network/sglang",
        "method": "Verify branch tip, immutable commit/tree, exported patch bytes and SHA256; exact selectors clean-apply in a temporary Git index to their target tree.",
        "results": results,
        "test_boundary": "Source/tree and export verification only. Linux imports, GPU execution, model-serving and production acceptance remain per-selector gates.",
    }
    encoded = canonical(verification)
    if args.check:
        assert VERIFICATION.read_bytes() == encoded, "selector verification record differs"
    else:
        VERIFICATION.write_bytes(encoded)
    print(json.dumps({
        "passed": True,
        "selectors": len(results),
        "exact_replays": sum(row["replay_mode"] == "exact" for row in results.values()),
        "expected_failures": sum(row["replay_mode"] == "expected_failure" for row in results.values()),
        "generated_patches": len(generated),
        "verification_sha256": sha256(encoded),
        "mode": "check" if args.check else "export-and-verify",
    }))


if __name__ == "__main__":
    main()
