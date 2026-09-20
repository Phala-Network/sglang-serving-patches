"""Verify source commits, exact exports, ordered application and complete engine trees.

Profiles are JSON (a YAML subset), so verification has no third-party dependency.
No checkout, refs, source worktree or runtime is modified; each profile uses a
private temporary Git index. Pass a local SGLang repository containing the
profile heads (fetch those explicit refs before running in CI).
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def verify(profile_path, source_repo):
    profile_path = Path(profile_path).resolve()
    root = profile_path.parents[2]
    profile = json.loads(profile_path.read_text(encoding="utf8"))
    with tempfile.TemporaryDirectory(prefix="sglang-profile-") as temp:
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(Path(temp) / "index")
        def git(*args, data=None):
            proc = subprocess.run(
                ["git", "-c", "core.autocrlf=false", "-c", "gc.auto=0", "-C", str(source_repo), *args],
                input=data, capture_output=True, env=env,
            )
            if proc.returncode:
                raise ValueError(proc.stderr.decode(errors="replace"))
            return proc.stdout
        git("read-tree", profile["upstream_commit"])
        seen = set()
        previous = profile["upstream_commit"]
        for patch in profile["patches"]:
            if patch["id"] in seen:
                raise ValueError("Duplicate patch: " + patch["id"])
            if not set(patch["depends_on"]) <= seen:
                raise ValueError("Missing or out-of-order dependency: " + patch["id"])
            path = (root / patch["path"]).resolve()
            if not path.is_relative_to(root):
                raise ValueError("Patch path escapes repository")
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != patch["sha256"]:
                raise ValueError("Patch bytes differ: " + patch["id"])
            actual_parent = git("rev-parse", patch["source_commit"] + "^").decode().strip()
            if actual_parent != patch["source_parent"] or actual_parent != previous:
                raise ValueError("Source parent/selection mismatch: " + patch["id"])
            exported = git("diff", "--binary", "--full-index", "--no-ext-diff", actual_parent, patch["source_commit"])
            if exported != data:
                raise ValueError("Source export mismatch: " + patch["id"])
            git("apply", "--cached", "--whitespace=nowarn", "-", data=data)
            actual_tree = git("write-tree").decode().strip()
            source_tree = git("rev-parse", patch["source_commit"] + "^{tree}").decode().strip()
            if actual_tree != source_tree or source_tree != patch["source_tree"]:
                raise ValueError("Applied source tree mismatch: " + patch["id"])
            seen.add(patch["id"])
            previous = patch["source_commit"]
        final_tree = git("write-tree").decode().strip()
        if final_tree != profile["expected_engine_tree"] or previous != profile["source_head"]:
            raise ValueError("Final tree/head mismatch")
        if profile["governor"]["enabled"]:
            raise ValueError("These historical profiles do not include Governor")
        return {"model": profile["model"], "patch_count": len(seen), "full_engine_tree": final_tree,
                "source_head": previous, "source_export_bytes_equal": True,
                "ordered_application_verified": True, "governor_enabled": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-repo", required=True)
    parser.add_argument("--profiles", nargs="+")
    parser.add_argument("--out")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    profiles = args.profiles or sorted((root / "profiles/v0.5.19").glob("*.yaml"))
    results = [verify(p, args.source_repo) for p in profiles]
    text = json.dumps(results, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf8")
    print(text)


if __name__ == "__main__":
    main()
