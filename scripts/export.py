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
ENGINE = "4281309187007db579a2195f40adfd4baa538528"
TREE = "83dcb00885129cc2afefdce2e169ebba697a9a67"
GOVERNOR = "631a53919c62e10c57e7b960bc4d443f39818276"
HOOK = "patches/sglang/v0.5.20/0001-governor-hooks.patch"
HOOK_SHA = "ebf6d2a2e8ef4c9a2c768803cbaf50eda7fc580ae0c888b9aff85297ef34b1a6"


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
    assert len(rows) == 31, "unexpected frozen source history"
    outputs, entries = {}, []
    previous = UPSTREAM
    for number, row in enumerate(rows, 1):
        commit, parent = row.split()
        assert parent == previous, "source history must be linear"
        title = git(source, "show", "-s", "--format=%s", commit).decode().strip()
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        if number == 31:
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
        "governor": {"commit": GOVERNOR, "hooks_only": True, "component_installation_required": True},
        "ordering": "apply_after records exact replay dependencies, not semantic dependence between unrelated fixes",
        "qualification": "See VALIDATION.md; source/tree reproduction does not imply model or final-image acceptance",
        "patches": entries,
        "selector_manifest": {
            "path": "selectors.json",
            "documentation": "SELECTOR_MANIFEST.md",
            "verification": "selector-verification.json",
            "model_selection_is_optional": True,
            "complete_engine_remains": "Phala-Network/sglang",
            "source_of_truth": "Phala-Network/sglang immutable fork commit/tree",
            "patches_are": "deterministic exports from fork commit ranges for audit/external consumers",
            "rebase_rule": "Rebase the fork source first, then regenerate selectors/patches and re-verify target trees; never hand-edit a parallel implementation",
        },
    }
    outputs["manifest.json"] = canonical(manifest)
    outputs["series"] = (
        "# Apply in order from pinned upstream; final entry is explicitly Governor-owned.\n"
        + "\n".join(entry["path"] for entry in entries)
        + "\n\n# Optional model selectors (see selectors.json; do not apply these to every model)\n"
        + "# kimi-k3-v0520-candidate: three shared common increments plus six Kimi-guarded patches\n"
        + "# muse-glimmer-v0520-candidate: the same three common increments plus one Muse-guarded patch\n"
        + "# deepseek-v4.1-v0520: blocked at dsv41-0011 until native closure recipe/ABI reconciliation\n"
        + "# Nemotron/Gemma/Qwen v0.5.19 selectors bind historical fork commits but are not v0.5.20 replays\n"
    ).encode()
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
    actual = {path.relative_to(ROOT).as_posix() for folder in ("patches", "integrations")
              for path in (ROOT / folder).rglob("*.patch")}
    selector_paths = {
        patch["path"]
        for selector in json.loads((ROOT / "selectors.json").read_text(encoding="utf-8"))["selectors"].values()
        for patch in selector.get("patches", [])
    }
    expected = {name for name in outputs if name.endswith(".patch")} | selector_paths
    external_path = ROOT / "external-dependencies.json"
    if external_path.exists():
        external = json.loads(external_path.read_text(encoding="utf-8"))["xgrammar"]
        expected.add(external["patch"])
        assert sha((ROOT / external["patch"]).read_bytes()) == external["patch_sha256"]
    missing = expected - actual
    assert not missing, "missing base/selector patch files: " + ", ".join(sorted(missing))
    historical_prefixes = tuple(
        f"patches/models/{family}/" for family in ("gemma", "muse", "nemotron", "qwen")
    )
    unexpected = {
        path
        for path in actual - expected
        if not path.startswith(historical_prefixes) and not path.startswith("patches/common/dsv41-")
    }
    assert not unexpected, "unexpected untracked patch files: " + ", ".join(sorted(unexpected))
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
                      "serving_patches": 30, "governor_hook_steps": 1,
                      "verified_intermediate_trees": len(manifest["patches"]),
                      "engine_commit": ENGINE, "engine_tree": TREE,
                      "manifest_sha256": sha(outputs["manifest.json"]),
                      "mode": "check" if args.check else "export-and-replay"}))


if __name__ == "__main__":
    main()
