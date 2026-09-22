"""Exercise real Git replay, including moved refs and failed patch evidence."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/export_selectors.py"
SPEC = importlib.util.spec_from_file_location("export_selectors", SCRIPT)
EXPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXPORT)


class SelectorReplayTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "source"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        self.base = self.commit("base\n")
        self.frozen = self.commit("frozen\n")
        self.target = self.commit("successor\n")
        self.git("branch", "moving-navigation", self.base)
        base_patch = self.export("base.patch", self.base, self.frozen)
        delta = self.export("delta.patch", self.frozen, self.target)
        tree = self.git("rev-parse", self.target + "^{tree}")
        frozen_tree = self.git("rev-parse", self.frozen + "^{tree}")
        self.document = {
            "upstream": self.base,
            "complete_engine_reference": {"commit": self.frozen, "tree": frozen_tree},
            "selectors": {
                "candidate": {
                    "fork_commit": self.target,
                    "fork_tree": tree,
                    "fork_branch": "moving-navigation",
                    "source_parent": self.frozen,
                    "patches": [delta],
                    "replay_mode": "exact",
                    "status": "source_only",
                }
            },
        }
        self.write_json("manifest.json", {
            "upstream": {"commit": self.base},
            "engine": {"commit": self.frozen, "tree": frozen_tree},
            "patches": [base_patch],
        })

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-c", "core.autocrlf=false", "-C", str(self.repo), *args],
            stderr=subprocess.PIPE,
        ).decode().strip()

    def commit(self, data):
        (self.repo / "value").write_text(data)
        self.git("add", "value")
        self.git("commit", "-qm", data.strip())
        return self.git("rev-parse", "HEAD")

    def export(self, name, parent, commit):
        _, data = EXPORT.export_patch(self.repo, commit)
        (self.root / name).write_bytes(data)
        return {"id": name, "path": name, "source_commit": commit,
                "sha256": EXPORT.sha256(data)}

    def write_json(self, name, value):
        (self.root / name).write_bytes(EXPORT.canonical(value))

    def run_export(self):
        self.write_json("selectors.json", self.document)
        with patch.multiple(EXPORT, ROOT=self.root,
                            SELECTORS=self.root / "selectors.json",
                            VERIFICATION=self.root / "verification.json"):
            with patch("sys.argv", ["export_selectors", "--source", str(self.repo)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    EXPORT.main()
        return json.loads((self.root / "verification.json").read_text())

    def test_moved_and_deleted_navigation_branch_do_not_change_identity(self):
        self.assertTrue(self.run_export()["results"]["candidate"]["passed"])
        self.git("branch", "-D", "moving-navigation")
        self.assertTrue(self.run_export()["results"]["candidate"]["passed"])

    def test_reference_identity_is_not_replay_pass(self):
        candidate = self.document["selectors"]["candidate"]
        candidate["replay_mode"] = "reference_only"
        candidate["patches"] = []
        result = self.run_export()["results"]["candidate"]
        self.assertIsNone(result["passed"])
        self.assertTrue(result["identity_verified"])
        self.assertNotIn("replay_tree", result)

    def test_corrupt_frozen_base_patch_fails(self):
        (self.root / "base.patch").write_bytes(b"corrupt")
        with self.assertRaises(AssertionError):
            self.run_export()

    def test_wrong_immutable_tree_fails(self):
        self.document["selectors"]["candidate"]["fork_tree"] = "0" * 40
        with self.assertRaises(AssertionError):
            self.run_export()

    def test_unverified_replay_base_fails(self):
        self.document["selectors"]["candidate"]["source_parent"] = self.base
        with self.assertRaises(AssertionError):
            self.run_export()

    def test_expected_failure_remains_failed(self):
        candidate = self.document["selectors"]["candidate"]
        candidate["patches"] *= 2
        candidate["replay_mode"] = "expected_failure"
        candidate["expected_failure_patch"] = "delta.patch"
        candidate["expected_applied_before_failure"] = 1
        result = self.run_export()["results"]["candidate"]
        self.assertFalse(result["passed"])
        self.assertEqual(result["applied_before_failure"], 1)

    def test_unknown_mode_fails_closed(self):
        self.document["selectors"]["candidate"]["replay_mode"] = "excat"
        with self.assertRaises(AssertionError):
            self.run_export()

    def native_manifest(self):
        patch = self.export("native.patch", self.frozen, self.target)
        return {
            "version": "0.2.6+phala.union1",
            "upstream_commit": self.frozen,
            "candidate_commit": self.target,
            "candidate_tree": self.git("rev-parse", self.target + "^{tree}"),
            "patch": patch["path"],
            "patch_sha256": patch["sha256"],
            "license_file": "value",
            "license_sha256": EXPORT.sha256(
                EXPORT.git(self.repo, "show", self.frozen + ":value").stdout
            ),
        }

    def test_external_delta_replays_without_public_candidate_ref(self):
        native = self.native_manifest()
        self.write_json("external-dependencies.json", {"xgrammar": native})
        result = self.run_export()["external_sources"]["xgrammar"]
        self.assertTrue(result["passed"])
        self.assertEqual(result["replay_tree"], native["candidate_tree"])

    def test_external_wrong_tree_or_license_is_rejected(self):
        for field in ("candidate_tree", "license_sha256"):
            with self.subTest(field=field):
                native = self.native_manifest()
                native[field] = "0" * len(native[field])
                self.write_json("external-dependencies.json", {"xgrammar": native})
                with self.assertRaises(AssertionError):
                    self.run_export()


if __name__ == "__main__":
    unittest.main()
