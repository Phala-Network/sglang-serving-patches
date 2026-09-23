#!/usr/bin/env python3
"""Replay, prepare and test the one active Phala SGLang patch stack."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

from export_selectors import canonical, export_patch, git, sha256

ROOT = Path(__file__).resolve().parents[1]


class StackError(ValueError):
    pass


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def local_path(root, value):
    if not isinstance(value, str):
        raise StackError("Expected a repository-relative path")
    path = Path(value)
    resolved = (root / path).resolve()
    if (
        path.is_absolute()
        or ".." in path.parts
        or not resolved.is_relative_to(root.resolve())
    ):
        raise StackError("Path leaves the patch or source repository")
    return resolved


def object_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise StackError("Expected an immutable 40-hex Git object")
    return value


def resolve(source, ref):
    return (
        git(source, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}")
        .stdout.decode()
        .strip()
    )


def read_stack(root=ROOT):
    if (root / "stack.json").exists():
        document = read_json(root / "stack.json")
        if document.get("schema") != "phala.sglang.unified-stack.v1":
            raise StackError("Unsupported unified stack schema")
        name = "unified"
        upstream = document["upstream"]["commit"]
        engine = document["engine"]
        engine_commit, engine_tree = engine["commit"], engine["tree"]
        patches = document["patches"]
        frozen_count, frozen_tree = 0, None
        previous = upstream
        for entry in patches:
            if entry.get("source_parent") != previous:
                raise StackError("Unified source commits must form one ordered chain")
            previous = object_id(entry["source_commit"])
        if previous != engine_commit:
            raise StackError("Unified source chain does not end at the engine")
        layout = "unified"
    else:
        document = read_json(root / "selectors.json")
        manifest = read_json(root / "manifest.json")
        name = document.get("active_selector")
        if not name or name not in document["selectors"]:
            raise StackError("One active_selector must be explicitly selected")
        active = document["selectors"][name]
        if active.get("replay_mode") != "exact":
            raise StackError("The active stack must have exact replay semantics")
        if (
            document["upstream"] != manifest["upstream"]["commit"]
            or document["complete_engine_reference"]["commit"]
            != manifest["engine"]["commit"]
            or document["complete_engine_reference"]["tree"]
            != manifest["engine"]["tree"]
            or active["source_parent"] != manifest["engine"]["commit"]
        ):
            raise StackError("Active successor does not bind the frozen base")
        upstream = document["upstream"]
        engine_commit, engine_tree = active["fork_commit"], active["fork_tree"]
        patches = manifest["patches"] + active["patches"]
        frozen_count, frozen_tree = len(manifest["patches"]), manifest["engine"]["tree"]
        layout = "legacy"
    for value in (upstream, engine_commit, engine_tree):
        object_id(value)
    seen, identifiers = set(), set()
    for entry in patches:
        identifier = entry["id"]
        if (
            not isinstance(identifier, str)
            or not identifier
            or identifier in identifiers
        ):
            raise StackError("Patch IDs must be nonempty and unique")
        identifiers.add(identifier)
        path = local_path(root, entry["path"])
        if path in seen:
            raise StackError("The active stack repeats a patch path")
        seen.add(path)
        if sha256(path.read_bytes()) != entry["sha256"]:
            raise StackError("Patch hash differs: " + entry["path"])
        if entry.get("source_commit"):
            object_id(entry["source_commit"])
    dependencies = {}
    if (root / "external-dependencies.json").exists():
        for dependency, spec in read_json(root / "external-dependencies.json").items():
            if dependency == "schema":
                if spec != "phala.external-source.v1":
                    raise StackError("Unsupported dependency manifest schema")
                continue
            if not isinstance(spec, dict):
                raise StackError("Invalid dependency record: " + dependency)
            path = local_path(root, spec["patch"])
            if sha256(path.read_bytes()) != spec["patch_sha256"]:
                raise StackError("Dependency patch hash differs: " + dependency)
            dependencies[dependency] = {
                "version": spec["version"],
                "patch_sha256": spec["patch_sha256"],
                "native_source_replay_and_build": "not-run-by-this-command",
            }
    return {
        "layout": layout,
        "active_selector": name,
        "upstream": upstream,
        "engine_commit": engine_commit,
        "engine_tree": engine_tree,
        "patches": patches,
        "dependencies": dependencies,
        "frozen_count": frozen_count,
        "frozen_tree": frozen_tree,
    }


def verify(source, root=ROOT):
    source = source.resolve()
    stack = read_stack(root)
    if resolve(source, stack["engine_commit"]) != stack["engine_commit"]:
        raise StackError("Engine commit did not resolve exactly")
    actual = (
        git(source, "rev-parse", stack["engine_commit"] + "^{tree}")
        .stdout.decode()
        .strip()
    )
    if actual != stack["engine_tree"]:
        raise StackError("Engine commit/tree identity differs")
    component_origins = []
    with tempfile.TemporaryDirectory(prefix="phala-stack-") as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / "index"))
        git(source, "read-tree", stack["upstream"], env=env)
        for index, entry in enumerate(stack["patches"], 1):
            if entry.get("source_commit"):
                parent, data = export_patch(source, entry["source_commit"])
                component = entry.get("component_source")
                if component:
                    if component["sha256"] != entry["sha256"] or not entry.get(
                        "result_tree"
                    ):
                        raise StackError(
                            "Component patch binding differs: " + entry["path"]
                        )
                    object_id(component["commit"])
                    component_origins.append(
                        {
                            "patch": entry["path"],
                            "origin": component,
                            "origin_repository_readback": "not-run-by-this-command",
                        }
                    )
                elif sha256(data) != entry["sha256"]:
                    raise StackError("Source-to-patch export differs: " + entry["path"])
                if entry.get("source_parent") and entry["source_parent"] != parent:
                    raise StackError("Source parent differs: " + entry["path"])
                if stack["layout"] == "unified":
                    parents = git(
                        source,
                        "rev-list",
                        "--parents",
                        "-n",
                        "1",
                        entry["source_commit"],
                    ).stdout.split()
                    if len(parents) != 2:
                        raise StackError(
                            "Unified patches must be single-parent commits"
                        )
                if entry.get("component_origin"):
                    component_origins.append(
                        {
                            "patch": entry["path"],
                            "origin": entry["component_origin"],
                            "origin_repository_readback": "not-run-by-this-command",
                            "rebased_patch_is_not_original_component_bytes": (
                                entry["sha256"] != entry["component_origin"]["sha256"]
                            ),
                        }
                    )
            git(
                source,
                "apply",
                "--cached",
                str(local_path(root, entry["path"])),
                env=env,
            )
            if entry.get("result_tree"):
                expected = (
                    git(source, "rev-parse", entry["source_commit"] + "^{tree}")
                    .stdout.decode()
                    .strip()
                )
                applied = git(source, "write-tree", env=env).stdout.decode().strip()
                if expected != entry["result_tree"] or applied != expected:
                    raise StackError(
                        "Intermediate source tree differs: " + entry["path"]
                    )
            if index == stack["frozen_count"]:
                tree = git(source, "write-tree", env=env).stdout.decode().strip()
                if tree != stack["frozen_tree"]:
                    raise StackError("Frozen base replay differs")
        tree = git(source, "write-tree", env=env).stdout.decode().strip()
    if tree != stack["engine_tree"]:
        raise StackError("Complete active replay differs")
    return {
        "status": "source-verified",
        "scope": "source-only",
        "active_selector": stack["active_selector"],
        "upstream": stack["upstream"],
        "engine_commit": stack["engine_commit"],
        "engine_tree": tree,
        "patch_count": len(stack["patches"]),
        "dependencies": stack["dependencies"],
        "component_origins": component_origins,
        "image_or_runtime_qualified": False,
    }


def upgrade_check(source, upstream, root=ROOT):
    verified = verify(source, root)
    stack = read_stack(root)
    target = resolve(source, upstream)
    records = []
    with tempfile.TemporaryDirectory(prefix="phala-upgrade-") as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / "index"))
        git(source, "read-tree", target, env=env)
        for entry in stack["patches"]:
            path = str(local_path(root, entry["path"]))
            row = {"id": entry["id"], "path": entry["path"]}
            if not git(
                source, "apply", "--cached", "--check", path, env=env, check=False
            ).returncode:
                git(source, "apply", "--cached", path, env=env)
                row["status"] = "applies"
            elif not git(
                source,
                "apply",
                "--cached",
                "--reverse",
                "--check",
                path,
                env=env,
                check=False,
            ).returncode:
                # Reverse application is evidence for review, not permission to
                # delete a patch or claim the entire behavior was upstreamed.
                row["status"] = "already-present-needs-review"
            else:
                row["status"] = "conflict"
                records.append(row)
                break
            records.append(row)
        tree = git(source, "write-tree", env=env).stdout.decode().strip()
    unresolved = [row for row in records if row["status"] != "applies"]
    return {
        "status": "needs-review" if unresolved else "ready-for-regression",
        "source_stack": verified,
        "requested_upstream": upstream,
        "target_upstream": target,
        "result_tree": tree,
        "patches": records,
        "unchecked_patch_count": len(stack["patches"]) - len(records),
        "changed_refs_or_worktree": False,
        "qualification": "No patch removal, build, regression or deployment was performed.",
        "decision_context": {
            "schema": "phala.sglang.upgrade-decisions.v1",
            "source_stack_sha256": sha256(canonical(stack)),
            "target_upstream": target,
            "patches": [],
        },
    }


def upgrade_decisions(path, stack, target):
    if path is None:
        return {}
    document = read_json(path)
    if (
        document.get("schema") != "phala.sglang.upgrade-decisions.v1"
        or document.get("source_stack_sha256") != sha256(canonical(stack))
        or document.get("target_upstream") != target
    ):
        raise StackError("Stale or invalid upgrade decision context")
    known = {entry["id"] for entry in stack["patches"]}
    decisions = {}
    for row in document["patches"]:
        identifier = row["id"]
        if identifier not in known or identifier in decisions:
            raise StackError("Unknown or duplicate upgrade decision ID")
        if row.get("action") not in {"replace", "drop"}:
            raise StackError("Upgrade decisions must replace or drop a patch")
        for field in ("reason", "evidence"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise StackError("Upgrade decisions require a reason and evidence")
        if row["action"] == "replace":
            object_id(row["source_commit"])
        decisions[identifier] = row
    return decisions


def export_upgrade(source, upstream, output, branch, decisions=None, root=ROOT):
    source, root = source.resolve(), root.resolve()
    if output.exists() or output.is_symlink():
        raise StackError("Upgrade export output must not already exist")
    output = output.resolve()
    if output.is_relative_to(source):
        raise StackError("Upgrade export output must be outside the source checkout")
    ref = "refs/heads/" + branch
    git(source, "check-ref-format", ref)
    if not git(source, "show-ref", "--verify", "--quiet", ref, check=False).returncode:
        raise StackError("Upgrade engine branch already exists")
    verify(source, root)
    stack = read_stack(root)
    target = resolve(source, upstream)
    choices = upgrade_decisions(decisions, stack, target)
    with tempfile.TemporaryDirectory(prefix="phala-reexport-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / "index"))
        git(source, "read-tree", target, env=env)
        previous, exported = target, []
        for entry in stack["patches"]:
            choice = choices.get(entry["id"])
            if choice and choice["action"] == "drop":
                continue
            current_tree = git(source, "write-tree", env=env).stdout.decode().strip()
            if choice:
                parents = git(
                    source, "rev-list", "--parents", "-n", "1", choice["source_commit"]
                ).stdout.split()
                if len(parents) != 2:
                    raise StackError("Replacement must be a single-parent commit")
                parent, data = export_patch(source, choice["source_commit"])
                parent_tree = (
                    git(source, "rev-parse", parent + "^{tree}").stdout.decode().strip()
                )
                if parent_tree != current_tree:
                    raise StackError(
                        "Replacement parent tree differs from the ordered prefix: "
                        + entry["id"]
                    )
            else:
                data = local_path(root, entry["path"]).read_bytes()
                if sha256(data) != entry["sha256"]:
                    raise StackError("Patch changed during export: " + entry["path"])
            candidate = Path(temporary) / "candidate.patch"
            candidate.write_bytes(data)
            checked = git(
                source,
                "apply",
                "--cached",
                "--check",
                str(candidate),
                env=env,
                check=False,
            )
            if checked.returncode:
                raise StackError(
                    "Patch conflicts or is already present; reviewed replace/drop "
                    "decision required: " + entry["id"]
                )
            git(source, "apply", "--cached", str(candidate), env=env)
            tree = git(source, "write-tree", env=env).stdout.decode().strip()
            message = (
                f"Reapply unified patch {entry['id']}\n\n"
                f"Previous patch SHA256: {entry['sha256']}\n"
                f"Target upstream: {target}"
            )
            commit = (
                git(source, "commit-tree", tree, "-p", previous, "-m", message)
                .stdout.decode()
                .strip()
            )
            parent, generated = export_patch(source, commit)
            patch_path = f"patches/{target[:12]}/{len(exported) + 1:04d}-{sha256(generated)[:12]}.patch"
            destination = local_path(staging, patch_path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(generated)
            row = {
                "id": entry["id"],
                "path": patch_path,
                "sha256": sha256(generated),
                "source_commit": commit,
                "source_parent": parent,
                "result_tree": tree,
                "origin": entry.get("origin")
                or {
                    key: entry[key]
                    for key in ("id", "path", "sha256", "source_commit")
                    if key in entry
                },
            }
            component = entry.get("component_source") or entry.get("component_origin")
            if component:
                row["component_origin"] = component
            exported.append(row)
            previous = commit
        tree = git(source, "write-tree", env=env).stdout.decode().strip()
        document = {
            "schema": "phala.sglang.unified-stack.v1",
            "upstream": {"commit": target},
            "engine": {"commit": previous, "tree": tree, "branch": branch},
            "previous_stack": {
                "upstream": stack["upstream"],
                "engine_commit": stack["engine_commit"],
                "sha256": sha256(canonical(stack)),
            },
            "reviewed_decisions": list(choices.values()),
            "patches": exported,
        }
        (staging / "stack.json").write_bytes(canonical(document))
        for filename in ("regressions.json", "external-dependencies.json"):
            origin = root / filename
            if origin.exists():
                (staging / filename).write_bytes(origin.read_bytes())
        dependency_file = staging / "external-dependencies.json"
        if dependency_file.exists():
            for name, spec in read_json(dependency_file).items():
                if name == "schema":
                    continue
                data = local_path(root, spec["patch"]).read_bytes()
                if sha256(data) != spec["patch_sha256"]:
                    raise StackError("Dependency changed during export: " + name)
                destination = local_path(staging, spec["patch"])
                if destination.exists():
                    raise StackError("Dependency path collides with generated files")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
        verified = verify(source, staging)
        if sha256(canonical(read_stack(root))) != document["previous_stack"]["sha256"]:
            raise StackError("Source patch stack changed during export")
        # Only verified artifacts leave the temporary directory. update-ref's
        # zero old ID prevents overwriting a branch created concurrently.
        shutil.copytree(staging, output)
        git(source, "update-ref", ref, previous, "0" * 40)
    result = {
        **verified,
        "status": "upgrade-exported-source-verified",
        "exported_stack": str(output),
        "engine_branch": branch,
        "upstream_changed": target != stack["upstream"],
        "reviewed_decision_count": len(choices),
        "tests_run": False,
        "qualification": "Local source export only; official release identity, decisions, regressions, dependencies, image and GPU acceptance require their own evidence.",
    }
    (output / "upgrade-result.json").write_bytes(canonical(result))
    return result


def prepare(source, output, root=ROOT, upstream=None):
    output = output.resolve()
    if output.exists():
        raise StackError("Prepare output must not already exist")
    if upstream is not None:
        result = upgrade_check(source, upstream, root)
        if result["status"] != "ready-for-regression":
            raise StackError(
                "Upgrade needs review; run upgrade-check for the patch report"
            )
        git(
            source,
            "worktree",
            "add",
            "--detach",
            "--",
            str(output),
            result["target_upstream"],
        )
        for entry in read_stack(root)["patches"]:
            git(output, "apply", "--index", str(local_path(root, entry["path"])))
        tree = git(output, "write-tree").stdout.decode().strip()
        if tree != result["result_tree"]:
            raise StackError(
                "Prepared upgrade tree differs; retained output: " + str(output)
            )
        return {
            "status": "upgrade-prepared-uncommitted",
            "scope": "source-only",
            "upstream": result["target_upstream"],
            "prepared_source": str(output),
            "result_tree": tree,
            "tests_run": False,
            "image_or_runtime_qualified": False,
        }
    verified = verify(source, root)
    git(
        source,
        "worktree",
        "add",
        "--detach",
        "--",
        str(output),
        verified["engine_commit"],
    )
    return {**verified, "prepared_source": str(output), "tests_run": False}


def junit_counts(path):
    document = ET.parse(path).getroot()
    cases = list(document.iter("testcase"))
    return {
        "tests": len(cases),
        "failures": sum(case.find("failure") is not None for case in cases),
        "errors": sum(case.find("error") is not None for case in cases),
        "skipped": sum(case.find("skipped") is not None for case in cases),
    }


def run_process(argv, source, env, log, timeout):
    # psutil is already a SGLang dependency. Keep timeout cleanup bounded to
    # this test's process tree, including workers that create their own group.
    import psutil

    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            argv, cwd=source, env=env, stdout=stream, stderr=subprocess.STDOUT
        )
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                parent = psutil.Process(process.pid)
                owned = parent.children(recursive=True) + [parent]
            except psutil.NoSuchProcess:
                owned = []
            for child in owned:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass
            _, alive = psutil.wait_procs(owned, timeout=10)
            for child in alive:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            psutil.wait_procs(alive, timeout=10)
            process.wait()
            return 124


def run_tests(source, output, suites, timeout, root=ROOT):
    source, output = source.resolve(), output.resolve()
    config = read_json(root / "regressions.json")
    cases = []
    for suite in suites:
        if suite not in config["suites"]:
            raise StackError("Unknown regression suite: " + suite)
        cases.extend((suite, case) for case in config["suites"][suite])
    if output.exists():
        raise StackError("Test output must be a fresh directory")
    if not cases or timeout <= 0:
        raise StackError("No tests selected or invalid timeout")
    names = set()
    for _, case in cases:
        if not re.fullmatch(r"[a-z0-9_-]+", case["name"]) or case["name"] in names:
            raise StackError("Test case names must be safe and unique")
        names.add(case["name"])
        if not local_path(source, case["path"]).is_file():
            raise StackError("Missing selected test: " + case["path"])
    top = git(source, "rev-parse", "--show-toplevel", check=False)
    identity = None
    if not top.returncode and Path(top.stdout.decode().strip()).resolve() == source:
        identity = {
            "commit": resolve(source, "HEAD"),
            "dirty": bool(git(source, "status", "--porcelain").stdout.strip()),
        }
    output.mkdir(parents=True)
    report = {
        "scope": "cpu-source-tests-not-image-or-gpu-acceptance",
        "tool_sha256": sha256(Path(__file__).read_bytes()),
        "regression_manifest_sha256": sha256((root / "regressions.json").read_bytes()),
        "source": str(source),
        "source_git": identity,
        "suites": suites,
        "cases": [],
        "status": "running",
    }
    env = dict(os.environ)
    env.update(
        CUDA_VISIBLE_DEVICES="",
        SGLANG_USE_CPU_ENGINE="1",
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        PYTHONDONTWRITEBYTECODE="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
    )
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(source / "tools/sglang-simulator/src"),
            str(source / "python"),
            str(source),
            env.get("PYTHONPATH", ""),
        ]
    )
    for suite, case in cases:
        directory = output / case["name"]
        directory.mkdir()
        xml, log = directory / "junit.xml", directory / "run.log"
        env["SGLANG_SIMULATOR_OUTPUT_DIR"] = str(directory / "metrics")
        env["SGLANG_SIMULATOR_OUTPUT_MODE"] = "OFFLINE"
        args = [
            "-q",
            "-s",
            "-p",
            "no:cacheprovider",
            "--junitxml=" + str(xml),
            "--basetemp=" + str(directory / "pytest"),
            case["path"],
            *case.get("args", []),
        ]
        if case.get("simulator_hooks"):
            argv = [
                sys.executable,
                "-c",
                "import sys; from sglang_simulator.simulation.sglang.hook_bootstrap "
                "import install_simulator_hooks; install_simulator_hooks(); "
                "import pytest; sys.exit(pytest.main(sys.argv[1:]))",
                *args,
            ]
        else:
            argv = [sys.executable, "-m", "pytest", *args]
        started = time.monotonic()
        code = run_process(argv, source, env, log, timeout)
        counts = None
        if xml.is_file():
            try:
                counts = junit_counts(xml)
            except ET.ParseError:
                pass
        status = "failed"
        if code == 0 and counts and not counts["failures"] and not counts["errors"]:
            status = (
                "passed"
                if counts["tests"] > 0 and not counts["skipped"]
                else "incomplete"
            )
        report["cases"].append(
            {
                "suite": suite,
                "name": case["name"],
                "path": case["path"],
                "status": status,
                "exit_code": code,
                "counts": counts,
                "duration_seconds": round(time.monotonic() - started, 3),
                "simulator_hooks": bool(case.get("simulator_hooks")),
                "log": str(log.relative_to(output)),
                "log_sha256": sha256(log.read_bytes()),
            }
        )
        (output / "result.json").write_bytes(canonical(report))
        if code == 124:
            break
    statuses = {case["status"] for case in report["cases"]}
    report["status"] = (
        "failed"
        if "failed" in statuses
        else "passed"
        if statuses == {"passed"} and len(report["cases"]) == len(cases)
        else "incomplete"
    )
    (output / "result.json").write_bytes(canonical(report))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect_command = commands.add_parser("inspect")
    inspect_command.add_argument("--stack-root", type=Path, default=ROOT)
    for name in ("verify", "upgrade-check", "upgrade-export", "prepare", "test"):
        command = commands.add_parser(name)
        command.add_argument("--stack-root", type=Path, default=ROOT)
        command.add_argument("--source", type=Path, required=True)
        command.add_argument("--output", type=Path, required=name != "verify")
        if name in ("upgrade-check", "upgrade-export", "prepare"):
            command.add_argument("--upstream", required=name != "prepare")
        if name == "upgrade-export":
            command.add_argument("--branch", required=True)
            command.add_argument("--decisions", type=Path)
        if name == "test":
            command.add_argument("--suite", action="append")
            command.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    try:
        if (
            args.command in ("verify", "upgrade-check")
            and args.output
            and args.output.exists()
        ):
            raise StackError("Report output already exists")
        if args.command == "inspect":
            stack = read_stack(args.stack_root)
            result = {key: value for key, value in stack.items() if key != "patches"}
            result["patches"] = [row["path"] for row in stack["patches"]]
        elif args.command == "verify":
            result = verify(args.source, args.stack_root)
        elif args.command == "upgrade-check":
            result = upgrade_check(args.source, args.upstream, args.stack_root)
        elif args.command == "upgrade-export":
            result = export_upgrade(
                args.source,
                args.upstream,
                args.output,
                args.branch,
                decisions=args.decisions,
                root=args.stack_root,
            )
        elif args.command == "prepare":
            result = prepare(
                args.source, args.output, args.stack_root, upstream=args.upstream
            )
        else:
            result = run_tests(
                args.source,
                args.output,
                args.suite or ["cpu"],
                args.timeout,
                args.stack_root,
            )
        if args.command in ("verify", "upgrade-check") and args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("xb") as stream:
                stream.write(canonical(result))
        print(json.dumps(result, indent=2))
        return (
            2 if result.get("status") in ("needs-review", "failed", "incomplete") else 0
        )
    except (StackError, OSError, RuntimeError, KeyError, json.JSONDecodeError) as error:
        print(f"stack: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
