import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("verifier", ROOT / "tools/verify_v0519_profiles.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ProfileVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "source"
        self.repo.mkdir()
        def git(*args):
            return subprocess.check_output(["git", "-c", "core.autocrlf=false", "-C", str(self.repo), *args]).decode().strip()
        self.git = git
        git("init", "-q")
        (self.repo / "python").mkdir()
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        (self.repo / "python/runtime.py").write_text("value = 1\n")
        git("add", "."); git("commit", "-qm", "base")
        base = git("rev-parse", "HEAD")
        (self.repo / "python/runtime.py").write_text("value = 2\n")
        git("commit", "-qam", "repair")
        head = git("rev-parse", "HEAD")
        tree = git("rev-parse", "HEAD^{tree}")
        raw = subprocess.check_output(["git", "-C", str(self.repo), "diff", "--binary", "--full-index", "--no-ext-diff", base, head])
        self.patch = self.root / "patches/fix.patch"; self.patch.parent.mkdir(); self.patch.write_bytes(raw)
        self.profile = self.root / "profiles/v0.5.19/model.yaml"; self.profile.parent.mkdir(parents=True)
        self.data = {"model":"fixture", "upstream_commit":base, "source_head":head, "expected_engine_tree":tree, "original_deployed_source":head,
            "governor":{"enabled":False}, "patches":[{"id":"fix", "depends_on":[], "path":"patches/fix.patch",
                "sha256":hashlib.sha256(raw).hexdigest(), "source_commit":head, "source_parent":base, "source_tree":tree, "original_commit":head, "original_parent":base, "files":["python/runtime.py"]}]}
    def run_verify(self):
        self.profile.write_text(json.dumps(self.data))
        return module.verify(self.profile, self.repo)
    def test_actual_application_matches_tree(self):
        self.assertEqual(self.run_verify()["patch_count"], 1)
    def test_tampered_bytes_rejected(self):
        self.patch.write_bytes(self.patch.read_bytes()+b"\n")
        with self.assertRaisesRegex(ValueError,"Patch bytes"): self.run_verify()
    def test_wrong_parent_rejected(self):
        self.data["patches"][0]["source_parent"] = self.data["source_head"]
        with self.assertRaisesRegex(ValueError,"parent/selection"): self.run_verify()
    def test_missing_dependency_rejected(self):
        self.data["patches"][0]["depends_on"] = ["not-selected"]
        with self.assertRaisesRegex(ValueError,"dependency"): self.run_verify()
    def test_wrong_tree_rejected(self):
        self.data["expected_engine_tree"] = "0"*40
        with self.assertRaisesRegex(ValueError,"Final tree"): self.run_verify()
    def test_duplicate_rejected(self):
        self.data["patches"].append(self.data["patches"][0].copy())
        with self.assertRaisesRegex(ValueError,"Duplicate"): self.run_verify()
    def test_export_not_just_hash_checked(self):
        raw=self.patch.read_bytes().replace(b"+value = 2",b"+value = 3")
        self.patch.write_bytes(raw);self.data["patches"][0]["sha256"]=hashlib.sha256(raw).hexdigest()
        with self.assertRaisesRegex(ValueError,"export mismatch"): self.run_verify()

if __name__ == "__main__": unittest.main()
