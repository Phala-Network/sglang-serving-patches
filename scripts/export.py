#!/usr/bin/env python3
"""Deterministic full-source export and clean Git-index replay; no model profiles."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "94602c9c2b7cbdb8efd5c52802dac6a1c180089e"
ENGINE = "354d47922eafa95ebc2d7bd63b7627d780a01c26"
TREE = "2733a3bae11d56e4bf3f694fbb49f8e9e156086d"
GOVERNOR = "675c5364bb103a6aacb12c26af406217cdd93622"
HOOK = "patches/sglang/v0.5.20/0001-governor-hooks.patch"
HOOK_SHA = "52087d47d575c95351e17e5335ac6ca5a3d5b6bb63548438502521ca524117ea"


def git(repo, *args, env=None):
    result = subprocess.run(["git", "-c", "core.autocrlf=false", "-C", str(repo), *args],
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return result.stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def export(source, governor):
    assert git(source, "rev-parse", ENGINE + "^{tree}").decode().strip() == TREE
    rows = git(source, "log", "--reverse", "--format=%H %P", UPSTREAM + ".." + ENGINE).decode().splitlines()
    assert len(rows) == 32, "unexpected frozen source history"
    outputs, entries = {}, []
    previous = UPSTREAM
    for number, row in enumerate(rows, 1):
        commit, parent = row.split()
        assert parent == previous, "source history must be linear"
        title = git(source, "show", "-s", "--format=%s", commit).decode().strip()
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        if number == 32:
            owner, scope, directory = "governor", "explicit-component-integration", "integrations/governor"
            data = git(governor, "show", GOVERNOR + ":" + HOOK)
            assert sha(data) == HOOK_SHA, "frozen Governor hook differs"
        else:
            owner = "serving"
            if number in (17, 18):
                scope, directory = "qwen-family", "patches/models/qwen"
            elif number in (21, 30):
                scope, directory = "glm-parser", "patches/models/glm"
            elif number == 27:
                scope, directory = "flashinfer-0.6.18-workspace", "patches/dependencies/flashinfer"
            else:
                scope, directory = "common-with-runtime-guards", "patches/common"
            data = git(source, "diff", "--binary", "--full-index", "--no-ext-diff", "--no-renames", parent, commit, "--")
        path = f"{directory}/{number:04d}-{slug}.patch"
        if owner == "governor":
            # Keep the public integration path stable when the complete-engine
            # commit title is refined; source commit/tree and bytes remain the
            # binding identities.
            path = "integrations/governor/0032-integrate-governor-tps-first-admission-v4.patch"
        outputs[path] = data
        entry = {"id": f"{number:04d}", "path": path, "owner": owner, "scope": scope,
                 "title": title, "source_commit": commit, "source_parent": parent,
                 "result_tree": git(source, "rev-parse", commit + "^{tree}").decode().strip(),
                 "apply_after": [] if not entries else [entries[-1]["id"]],
                 "sha256": sha(data),
                 "changed_files": git(source, "diff", "--name-only", parent, commit).decode().splitlines()}
        if owner == "governor":
            entry["component_source"] = {"repository": "https://github.com/Phala-Network/phala-inference-governor",
                                         "commit": GOVERNOR, "path": HOOK, "sha256": HOOK_SHA}
        entries.append(entry)
        previous = commit
    manifest = {
        "schema": "phala.sglang.source-export.v1",
        "upstream": {"repository": "https://github.com/sgl-project/sglang", "tag": "v0.5.20", "commit": UPSTREAM},
        "engine": {"repository": "https://github.com/Phala-Network/sglang", "commit": ENGINE, "tree": TREE},
        "serving_result": {"commit": entries[-2]["source_commit"], "tree": entries[-2]["result_tree"]},
        "governor": {
            "commit": GOVERNOR,
            "version": "0.2.2",
            "abi_version": 4,
            "hooks_only": True,
            "component_installation_required": True,
        },
        "historical_governor": {
            "archive": "history/governor-v0.1.1",
            "commit": "631a53919c62e10c57e7b960bc4d443f39818276",
            "hook_sha256": "ebf6d2a2e8ef4c9a2c768803cbaf50eda7fc580ae0c888b9aff85297ef34b1a6",
            "engine_commit": "4281309187007db579a2195f40adfd4baa538528",
            "engine_tree": "83dcb00885129cc2afefdce2e169ebba697a9a67",
        },
        "ordering": "apply_after records exact replay dependencies, not semantic dependence between unrelated fixes",
        "qualification": "See VALIDATION.md; source/tree reproduction does not imply model or final-image acceptance",
        "patches": entries,
    }
    outputs["manifest.json"] = canonical(manifest)
    outputs["series"] = ("# Apply in order from pinned upstream; final entry is explicitly Governor-owned.\n" +
                         "\n".join(entry["path"] for entry in entries) + "\n").encode()
    return outputs, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--governor", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="verify committed export bytes without changing files")
    args = parser.parse_args()
    outputs, manifest = export(args.source, args.governor)
    for name, data in outputs.items():
        target = ROOT / name
        if args.check:
            assert target.read_bytes() == data, "generated bytes differ: " + name
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    # Model selectors and historical compatibility inputs may keep additional
    # patch files outside the active complete-engine series. Governor has one
    # active integration step, so reject stale or duplicate files there while
    # allowing selector-owned patches to coexist under patches/.
    actual_integrations = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "integrations").rglob("*.patch")
    }
    expected_integrations = {
        name
        for name in outputs
        if name.startswith("integrations/") and name.endswith(".patch")
    }
    assert actual_integrations == expected_integrations, (
        "unexpected or missing active Governor integration patch files"
    )
    with tempfile.TemporaryDirectory(prefix="sglang-export-replay-") as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / "index"))
        git(args.source, "read-tree", UPSTREAM, env=env)
        for entry in manifest["patches"]:
            path = str((ROOT / entry["path"]).resolve())
            git(args.source, "apply", "--cached", "--check", path, env=env)
            git(args.source, "apply", "--cached", path, env=env)
            actual_tree = git(args.source, "write-tree", env=env).decode().strip()
            assert actual_tree == entry["result_tree"], "replay tree differs: " + entry["id"]
        assert actual_tree == TREE
    print(json.dumps({"passed": True, "patches": len(manifest["patches"]),
                      "serving_patches": 31, "governor_hook_steps": 1,
                      "verified_intermediate_trees": len(manifest["patches"]),
                      "engine_commit": ENGINE, "engine_tree": TREE,
                      "manifest_sha256": sha(outputs["manifest.json"]),
                      "mode": "check" if args.check else "export-and-replay"}))


if __name__ == "__main__":
    main()
