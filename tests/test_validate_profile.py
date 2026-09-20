import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_profile import EXPORT_ARGS, export, git, sha, validate


class ProfileValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        git(self.source, "init")
        git(self.source, "config", "user.name", "Fixture")
        git(self.source, "config", "user.email", "fixture@example.invalid")
        git(self.source, "config", "core.autocrlf", "false")
        (self.source / "base").write_bytes(b"base\n")
        self.base = self.commit("base")
        items = []
        parent = self.base
        for name in ("a", "b", "unused"):
            (self.source / name).write_bytes((name + "\n").encode())
            commit = self.commit(name)
            raw = export(self.source, parent, commit)
            (self.root / (name + ".patch")).write_bytes(raw)
            items.append({"id": name, "path": name + ".patch", "sha256": sha(raw), "source_commit": commit, "source_parent": parent, "source_tree": git(self.source, "rev-parse", commit + "^{tree}").decode().strip(), "dependencies": ["a"] if name == "b" else [], "conflicts_with_source_commits": []})
            parent = commit
        self.catalog = {"base_commit": self.base, "export_argv": EXPORT_ARGS, "export_argv_sha256": sha(json.dumps(EXPORT_ARGS, separators=(",", ":")).encode()), "patches": items}
        self.profile = {"catalog": "catalog.json", "governor": {"enabled": False}, "upstream": {"commit": self.base}, "expected_tree": items[1]["source_tree"], "patches": [{k: item[k] for k in ("id", "path", "sha256", "dependencies")} for item in items[:2]]}

    def commit(self, message):
        git(self.source, "add", ".")
        git(self.source, "commit", "-m", message)
        return git(self.source, "rev-parse", "HEAD").decode().strip()

    def run_validation(self):
        (self.root / "profile.yaml").write_text(json.dumps(self.profile), encoding="utf-8")
        (self.root / "catalog.json").write_text(json.dumps(self.catalog), encoding="utf-8")
        return validate(self.root, "profile.yaml", self.source)

    def test_valid_and_unselected_common_is_not_applied(self):
        receipt = self.run_validation()
        self.assertEqual(receipt["actual_tree"], self.catalog["patches"][1]["source_tree"])
        self.assertEqual([p["id"] for p in receipt["patches"]], ["a", "b"])

    def test_patch_tampering(self):
        (self.root / "a.patch").write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "export bytes"):
            self.run_validation()

    def test_parent_tampering(self):
        self.catalog["patches"][1]["source_parent"] = self.base
        with self.assertRaisesRegex(ValueError, "source parent"):
            self.run_validation()

    def test_missing_dependency(self):
        self.profile["patches"] = self.profile["patches"][1:]
        with self.assertRaisesRegex(ValueError, "missing or out-of-order"):
            self.run_validation()

    def test_undeclared_dependency(self):
        self.profile["patches"][1]["dependencies"] = []
        with self.assertRaisesRegex(ValueError, "dependency declaration"):
            self.run_validation()

    def test_dependency_order(self):
        self.profile["patches"].reverse()
        with self.assertRaisesRegex(ValueError, "missing or out-of-order"):
            self.run_validation()

    def test_wrong_expected_tree(self):
        self.profile["expected_tree"] = self.catalog["patches"][2]["source_tree"]
        with self.assertRaisesRegex(ValueError, "final tree"):
            self.run_validation()

    def test_mutual_exclusion(self):
        self.catalog["patches"][0]["conflicts_with_source_commits"] = [self.catalog["patches"][1]["source_commit"]]
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            self.run_validation()

    def test_unknown_patch(self):
        self.profile["patches"][0]["id"] = "unknown"
        with self.assertRaisesRegex(ValueError, "undeclared patch"):
            self.run_validation()

    def test_crlf_patch_is_rejected(self):
        path = self.root / "a.patch"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        with self.assertRaisesRegex(ValueError, "export bytes"):
            self.run_validation()

    def test_profile_raw_hash_preserves_line_endings(self):
        first = self.run_validation()
        path = self.root / "profile.yaml"
        path.write_bytes(json.dumps(self.profile, indent=2).replace("\n", "\r\n").encode())
        second = validate(self.root, "profile.yaml", self.source)
        self.assertEqual(first["actual_tree"], second["actual_tree"])
        self.assertNotEqual(first["profile_sha256"], second["profile_sha256"])

    def test_parent_ancestry_does_not_implicitly_select_patch(self):
        # b was committed on top of a, but its independent delta can stand alone
        # when its declared semantic dependency is deliberately removed in fixture.
        self.catalog["patches"][1]["dependencies"] = []
        self.profile["patches"] = [copy.deepcopy(self.profile["patches"][1])]
        self.profile["patches"][0]["dependencies"] = []
        with self.assertRaisesRegex(ValueError, "final tree"):
            self.run_validation()

if __name__ == "__main__":
    unittest.main()
