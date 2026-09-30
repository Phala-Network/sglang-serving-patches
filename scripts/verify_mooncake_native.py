"""Verify the independent Mooncake patch against its public immutable base."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "native/mooncake/manifest.json").read_text())
    assert manifest["schema"] == "phala.mooncake.independent-source.v1"
    assert manifest["upstream_repository"] == "https://github.com/kvcache-ai/Mooncake"
    for name in ("base_commit", "source_commit", "source_tree"):
        assert re.fullmatch(r"[0-9a-f]{40}", manifest[name])
    patch = None
    if manifest.get("patch"):
        relative = Path(manifest["patch"])
        assert not relative.is_absolute() and ".." not in relative.parts
        patch = ROOT / relative
        assert hashlib.sha256(patch.read_bytes()).hexdigest() == manifest["patch_sha256"]
    else:
        assert not manifest.get("patch_sha256"), "unpatched source has a stale patch hash"
    with tempfile.TemporaryDirectory(prefix="mooncake-patch-replay-") as temporary:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temporary) / "index"))
        prefix = ["git", "-c", "core.autocrlf=false", "-C", str(args.source)]
        subprocess.run(prefix + ["read-tree", manifest["base_commit"]], env=env, check=True)
        if patch is not None:
            subprocess.run(prefix + ["apply", "--cached", str(patch.resolve())], env=env, check=True)
        tree = subprocess.check_output(prefix + ["write-tree"], env=env, text=True).strip()
        assert tree == manifest["source_tree"]
    print(json.dumps({"passed": True, "scope": "native-source-only", "source_tree": tree, "patch_sha256": manifest.get("patch_sha256")}))


if __name__ == "__main__":
    main()
