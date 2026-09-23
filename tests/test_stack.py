"""Real-Git contracts for the active stack and structured test-result gates."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("active_stack", SCRIPTS / "stack.py")
STACK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STACK)


class StackTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.base = self.commit("base\n")
        self.frozen = self.commit("frozen\n")
        self.engine = self.commit("complete\n")
        first = self.export("base.patch", self.frozen)
        second = self.export("delta.patch", self.engine)
        frozen = {"commit": self.frozen, "tree": self.tree(self.frozen)}
        self.manifest = {
            "upstream": {"commit": self.base},
            "engine": frozen,
            "patches": [first],
        }
        self.document = {
            "active_selector": "unified",
            "upstream": self.base,
            "complete_engine_reference": {"repository": "fixture", **frozen},
            "selectors": {
                "unified": {
                    "fork_commit": self.engine,
                    "fork_tree": self.tree(self.engine),
                    "source_parent": self.frozen,
                    "replay_mode": "exact",
                    "patches": [second],
                }
            },
        }
        self.write_inputs()

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-c", "core.autocrlf=false", "-C", str(self.source), *args],
            stderr=subprocess.PIPE,
            text=True,
        ).strip()

    def tree(self, commit):
        return self.git("rev-parse", commit + "^{tree}")

    def commit(self, text):
        (self.source / "value").write_text(text)
        self.git("add", "value")
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def export(self, name, commit):
        parent, data = STACK.export_patch(self.source, commit)
        (self.root / name).write_bytes(data)
        return {
            "id": name,
            "path": name,
            "source_commit": commit,
            "source_parent": parent,
            "sha256": STACK.sha256(data),
        }

    def write_inputs(self):
        (self.root / "selectors.json").write_bytes(STACK.canonical(self.document))
        (self.root / "manifest.json").write_bytes(STACK.canonical(self.manifest))

    def test_complete_stack_replays_without_touching_user_index_or_checkout(self):
        (self.source / "local").write_text("keep staged edits\n")
        self.git("add", "local")
        before = self.git("write-tree")
        result = STACK.verify(self.source, self.root)
        self.assertEqual(result["patch_count"], 2)
        self.assertEqual(result["engine_tree"], self.tree(self.engine))
        self.assertEqual(self.git("write-tree"), before)
        self.assertEqual((self.source / "local").read_text(), "keep staged edits\n")
        self.assertFalse(result["image_or_runtime_qualified"])

    def test_active_selector_must_be_explicit_and_exact(self):
        del self.document["active_selector"]
        self.write_inputs()
        with self.assertRaises(STACK.StackError):
            STACK.read_stack(self.root)
        self.document["active_selector"] = "unified"
        self.document["selectors"]["unified"]["replay_mode"] = "reference_only"
        self.write_inputs()
        with self.assertRaises(STACK.StackError):
            STACK.read_stack(self.root)

    def test_wrong_binding_or_changed_patch_is_rejected(self):
        self.document["selectors"]["unified"]["source_parent"] = self.base
        self.write_inputs()
        with self.assertRaises(STACK.StackError):
            STACK.verify(self.source, self.root)
        self.document["selectors"]["unified"]["source_parent"] = self.frozen
        self.write_inputs()
        (self.root / "delta.patch").write_bytes(b"corrupt")
        with self.assertRaises(STACK.StackError):
            STACK.verify(self.source, self.root)

    def test_source_export_identity_is_verified(self):
        self.document["selectors"]["unified"]["patches"][0]["source_commit"] = (
            self.frozen
        )
        self.write_inputs()
        with self.assertRaisesRegex(STACK.StackError, "Source-to-patch"):
            STACK.verify(self.source, self.root)

    def test_wrong_engine_tree_is_rejected(self):
        self.document["selectors"]["unified"]["fork_tree"] = self.tree(self.base)
        self.write_inputs()
        with self.assertRaisesRegex(STACK.StackError, "identity differs"):
            STACK.verify(self.source, self.root)

    def test_patch_path_cannot_escape_root(self):
        self.document["selectors"]["unified"]["patches"][0]["path"] = "../outside.patch"
        self.write_inputs()
        with self.assertRaisesRegex(STACK.StackError, "leaves"):
            STACK.read_stack(self.root)

    def test_duplicate_patch_is_rejected(self):
        self.document["selectors"]["unified"]["patches"].append(
            self.manifest["patches"][0]
        )
        self.write_inputs()
        with self.assertRaisesRegex(STACK.StackError, "repeats"):
            STACK.read_stack(self.root)

    def test_upgrade_preserves_unrelated_new_upstream_changes(self):
        self.git("switch", "--detach", self.base)
        (self.source / "new-upstream-file").write_text("new upstream\n")
        self.git("add", "new-upstream-file")
        self.git("commit", "-qm", "new upstream")
        upstream = self.git("rev-parse", "HEAD")
        result = STACK.upgrade_check(self.source, upstream, self.root)
        self.assertEqual(result["status"], "ready-for-regression")
        self.assertEqual(result["unchecked_patch_count"], 0)
        self.assertEqual(self.git("show", result["result_tree"] + ":value"), "complete")
        self.assertEqual(
            self.git("show", result["result_tree"] + ":new-upstream-file"),
            "new upstream",
        )
        self.assertEqual(self.git("rev-parse", "HEAD"), upstream)
        self.assertEqual((self.source / "value").read_text(), "base\n")

    def test_already_present_patch_requires_review_not_silent_removal(self):
        result = STACK.upgrade_check(self.source, self.frozen, self.root)
        self.assertEqual(result["status"], "needs-review")
        self.assertEqual(result["patches"][0]["status"], "already-present-needs-review")
        self.assertEqual(result["result_tree"], self.tree(self.engine))
        self.assertEqual(len(STACK.read_stack(self.root)["patches"]), 2)

    def test_conflict_stops_before_dependent_patches(self):
        self.git("switch", "--detach", self.base)
        upstream = self.commit("incompatible\n")
        result = STACK.upgrade_check(self.source, upstream, self.root)
        self.assertEqual(result["status"], "needs-review")
        self.assertEqual(result["patches"][0]["status"], "conflict")
        self.assertEqual(result["unchecked_patch_count"], 1)
        self.assertEqual(result["result_tree"], self.tree(upstream))
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_prepare_creates_only_a_new_detached_checkout(self):
        target = self.root / "prepared"
        result = STACK.prepare(self.source, target, self.root)
        self.assertEqual((target / "value").read_text(), "complete\n")
        self.assertEqual(result["engine_commit"], self.engine)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.engine)
        with self.assertRaises(STACK.StackError):
            STACK.prepare(self.source, target, self.root)

    def test_prepare_upgrade_stages_one_combined_candidate(self):
        self.git("switch", "--detach", self.base)
        (self.source / "new-upstream-file").write_text("new upstream\n")
        self.git("add", "new-upstream-file")
        self.git("commit", "-qm", "new upstream")
        upstream = self.git("rev-parse", "HEAD")
        target = self.root / "prepared-upgrade"
        result = STACK.prepare(self.source, target, self.root, upstream=upstream)
        self.assertEqual(result["status"], "upgrade-prepared-uncommitted")
        self.assertEqual((target / "value").read_text(), "complete\n")
        self.assertEqual((target / "new-upstream-file").read_text(), "new upstream\n")
        self.assertEqual(self.git("rev-parse", "HEAD"), upstream)
        self.assertEqual((self.source / "value").read_text(), "base\n")

    def test_prepare_does_not_create_a_checkout_when_review_is_needed(self):
        target = self.root / "should-not-exist"
        with self.assertRaisesRegex(STACK.StackError, "needs review"):
            STACK.prepare(self.source, target, self.root, upstream=self.frozen)
        self.assertFalse(target.exists())

    def setup_regression(self):
        (self.source / "test_fixture.py").write_text("def test_ok(): pass\n")
        config = {"suites": {"cpu": [{"name": "one", "path": "test_fixture.py"}]}}
        (self.root / "regressions.json").write_bytes(STACK.canonical(config))

    def test_runner_rejects_zero_tests_skips_and_failure_even_with_exit_zero(self):
        self.setup_regression()
        for index, (body, expected) in enumerate(
            (
                ("<testcase name='ok'/>", "passed"),
                ("", "incomplete"),
                ("<testcase name='skip'><skipped/></testcase>", "incomplete"),
                ("<testcase name='bad'><failure/></testcase>", "failed"),
            )
        ):

            def run(argv, source, env, log, timeout):
                self.assertEqual(env["CUDA_VISIBLE_DEVICES"], "")
                self.assertEqual(env["SGLANG_USE_CPU_ENGINE"], "1")
                log.write_text("fixture output\n")
                (log.parent / "junit.xml").write_text(
                    "<testsuite>" + body + "</testsuite>"
                )
                return 0

            with patch.object(STACK, "run_process", side_effect=run):
                report = STACK.run_tests(
                    self.source, self.root / f"results-{index}", ["cpu"], 60, self.root
                )
            self.assertEqual(report["status"], expected)

    def test_runner_cannot_overwrite_previous_evidence(self):
        self.setup_regression()
        target = self.root / "prior"
        target.mkdir()
        with self.assertRaises(STACK.StackError):
            STACK.run_tests(self.source, target, ["cpu"], 60, self.root)

    def test_dependency_patch_integrity_is_checked_separately(self):
        data = (self.root / "delta.patch").read_bytes()
        spec = {
            "version": "fixture",
            "patch": "delta.patch",
            "patch_sha256": STACK.sha256(data),
        }
        (self.root / "external-dependencies.json").write_bytes(
            STACK.canonical({"schema": "phala.external-source.v1", "native": spec})
        )
        dependency = STACK.verify(self.source, self.root)["dependencies"]["native"]
        self.assertEqual(
            dependency["native_source_replay_and_build"], "not-run-by-this-command"
        )
        spec["patch_sha256"] = "0" * 64
        (self.root / "external-dependencies.json").write_bytes(
            STACK.canonical({"native": spec})
        )
        with self.assertRaises(STACK.StackError):
            STACK.verify(self.source, self.root)

    def test_component_patch_format_can_differ_but_exact_source_tree_must_match(self):
        entry = self.manifest["patches"][0]
        path = self.root / entry["path"]
        lines = path.read_bytes().decode().splitlines(keepends=True)
        data = "".join(
            line for line in lines if not line.startswith(("diff --git ", "index "))
        ).encode()
        path.write_bytes(data)
        entry["sha256"] = STACK.sha256(data)
        entry["result_tree"] = self.tree(self.frozen)
        entry["component_source"] = {
            "repository": "component-fixture",
            "commit": self.frozen,
            "path": "owned.patch",
            "sha256": entry["sha256"],
        }
        self.write_inputs()
        result = STACK.verify(self.source, self.root)
        self.assertEqual(
            result["component_origins"][0]["origin_repository_readback"],
            "not-run-by-this-command",
        )
        entry["result_tree"] = self.tree(self.base)
        self.write_inputs()
        with self.assertRaisesRegex(STACK.StackError, "Intermediate"):
            STACK.verify(self.source, self.root)


if __name__ == "__main__":
    unittest.main()
