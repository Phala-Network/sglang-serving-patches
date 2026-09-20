"""Verify JSON-compatible YAML profiles against immutable Git source objects."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

EXPORT_ARGS = ["-c", "core.autocrlf=false", "-c", "core.quotePath=true", "diff", "--no-ext-diff", "--no-textconv", "--binary", "--full-index", "--no-renames", "--diff-algorithm=myers", "--no-indent-heuristic", "--unified=3", "--src-prefix=a/", "--dst-prefix=b/", "--no-color"]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(source, *args, env=None, data=None):
    return subprocess.run(["git", "-C", str(source), *args], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, env=env).stdout

def export(source, parent, commit):
    return git(source, *EXPORT_ARGS, parent, commit, "--")

def contained(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("path escapes repository")
    return path

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(root, profile_path, source):
    root, source = Path(root), Path(source)
    raw = contained(root, profile_path).read_bytes()
    profile = json.loads(raw)
    catalog_raw = contained(root, profile["catalog"]).read_bytes()
    catalog = json.loads(catalog_raw)
    require(catalog["export_argv"] == EXPORT_ARGS, "unsupported export command")
    require(catalog["export_argv_sha256"] == sha(json.dumps(EXPORT_ARGS, separators=(",", ":")).encode()), "export command hash mismatch")
    require(profile["governor"]["enabled"] is False, "Governor composition is not supported by this validator")
    require(profile["upstream"]["commit"] == catalog["base_commit"], "base mismatch")
    items = catalog["patches"]
    require(len({i["id"] for i in items}) == len(items), "duplicate catalog id")
    entries = {i["id"]: i for i in items}
    selected = profile["patches"]
    ids = [i["id"] for i in selected]
    require(len(set(ids)) == len(ids), "duplicate selection")
    require(all(i in entries for i in ids), "undeclared patch")
    commits = {entries[i]["source_commit"] for i in ids}
    seen, receipts, patches = set(), [], []
    for chosen in selected:
        item = entries[chosen["id"]]
        require(chosen["dependencies"] == item["dependencies"], "dependency declaration mismatch")
        require(set(item["dependencies"]) <= seen, "missing or out-of-order dependency")
        require(not set(item.get("conflicts_with_source_commits", [])) & commits, "mutually exclusive patches")
        require(chosen["path"] == item["path"], "patch path mismatch")
        require(chosen["sha256"] == item["sha256"], "catalog hash mismatch")
        parent, commit = item["source_parent"], item["source_commit"]
        actual = git(source, "rev-list", "--parents", "-n", "1", commit).decode().strip().split()
        require(actual == [commit, parent], "source parent mismatch")
        tree = git(source, "rev-parse", commit + "^{tree}").decode().strip()
        require(tree == item["source_tree"], "source tree mismatch")
        patch = contained(root, chosen["path"]).read_bytes()
        require(patch == export(source, parent, commit), "export bytes mismatch")
        require(sha(patch) == chosen["sha256"], "patch hash mismatch")
        patches.append(patch)
        receipts.append({"id": item["id"], "source_commit": commit, "source_parent": parent, "source_tree": tree, "patch_sha256": sha(patch), "bytes": len(patch)})
        seen.add(item["id"])
    with tempfile.TemporaryDirectory(prefix="profile-index-") as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / "index"))
        git(source, "read-tree", profile["upstream"]["commit"], env=env)
        for patch in patches:
            git(source, "-c", "core.autocrlf=false", "apply", "--cached", "--whitespace=nowarn", "-", env=env, data=patch)
        tree = git(source, "write-tree", env=env).decode().strip()
    require(tree == profile["expected_tree"], "final tree mismatch: " + tree)
    return {"schema": "phala.profile-validation-receipt.v1", "profile": profile_path, "profile_sha256": sha(raw), "catalog_sha256": sha(catalog_raw), "base_commit": profile["upstream"]["commit"], "actual_tree": tree, "expected_tree": profile["expected_tree"], "export_argv": EXPORT_ARGS, "patches": receipts, "scope": "source export and selected composition only; no runtime or approval claim"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--profile", default="profiles/v0.5.20/kimi-k3.yaml")
    parser.add_argument("--source", required=True)
    parser.add_argument("--receipt")
    args = parser.parse_args()
    result = json.dumps(validate(args.root, args.profile, args.source), indent=2) + "\n"
    if args.receipt:
        Path(args.receipt).write_text(result, encoding="utf-8", newline="\n")
    print(result, end="")

if __name__ == "__main__":
    main()
