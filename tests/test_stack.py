"""Real-Git contracts for the active stack and structured test-result gates."""

import importlib.util
import json
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

    def git_ok(self, *args):
        return (
            subprocess.run(
                ["git", "-c", "core.autocrlf=false", "-C", str(self.source), *args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).returncode
            == 0
        )

    def source_snapshot(self):
        return {
            "head": self.git("rev-parse", "HEAD"),
            "tree": self.git("write-tree"),
            "status": self.git("status", "--porcelain"),
        }

    def make_upstream_commit(self, parent, filename, text):
        original = self.git("rev-parse", "HEAD")
        self.git("switch", "--detach", parent)
        (self.source / filename).write_text(text)
        self.git("add", filename)
        self.git("commit", "-qm", "unrelated upstream")
        commit = self.git("rev-parse", "HEAD")
        self.git("switch", "--detach", original)
        return commit

    def make_replacement_commit(self, parent, message="replacement origin"):
        original = self.git("rev-parse", "HEAD")
        self.git("switch", "--detach", parent)
        (self.source / "value").write_text("frozen\n")
        self.git("add", "value")
        self.git("commit", "--allow-empty", "-qm", message)
        commit = self.git("rev-parse", "HEAD")
        self.git("switch", "--detach", original)
        return commit

    def stack_sha(self, root=None):
        root = root or self.root
        return STACK.sha256(STACK.canonical(STACK.read_stack(root)))

    def write_decisions(
        self, target_upstream, patches, root=None, name="decisions.json"
    ):
        root = root or self.root
        decisions = {
            "schema": "phala.sglang.upgrade-decisions.v1",
            "source_stack_sha256": self.stack_sha(root),
            "target_upstream": target_upstream,
            "patches": patches,
        }
        path = root / name
        path.write_bytes(STACK.canonical(decisions))
        return path

    def patch_ids(self):
        return [
            self.manifest["patches"][0]["id"],
            self.document["selectors"]["unified"]["patches"][0]["id"],
        ]

    def assert_flat_stack(self, output, result):
        stack_path = output / "stack.json"
        self.assertTrue(stack_path.is_file())
        document = json.loads(stack_path.read_text())
        self.assertTrue({"upstream", "engine", "patches"}.issubset(document))
        self.assertEqual(document["schema"], "phala.sglang.unified-stack.v1")
        self.assertEqual(document["engine"]["commit"], result["engine_commit"])
        self.assertEqual(document["engine"]["tree"], result["engine_tree"])
        self.assertFalse((output / "selectors.json").exists())
        self.assertFalse((output / "manifest.json").exists())
        parsed = STACK.read_stack(output)
        self.assertEqual(parsed["engine_tree"], result["engine_tree"])
        self.assertEqual(
            STACK.verify(self.source, output)["engine_tree"], result["engine_tree"]
        )
        return document, parsed

    def assert_linear_patch_origins(self, document):
        previous = document["upstream"]["commit"]
        originals = {
            entry["id"]: entry for entry in STACK.read_stack(self.root)["patches"]
        }
        for entry in document["patches"]:
            self.assertRegex(entry["id"], r"^[0-9A-Za-z._-]+$")
            self.assertEqual(entry["source_parent"], previous)
            generated = entry["source_commit"]
            self.assertRegex(generated, r"^[0-9a-f]{40}$")
            self.assertEqual(
                entry["origin"],
                {
                    key: originals[entry["id"]][key]
                    for key in ("id", "path", "sha256", "source_commit")
                },
            )
            self.assertEqual(
                self.git("rev-list", "--parents", "-n", "1", generated).split(),
                [generated, previous],
            )
            previous = generated
        self.assertEqual(previous, document["engine"]["commit"])

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
        with self.assertRaisesRegex(
            STACK.StackError, "repeats|IDs must be nonempty and unique"
        ):
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

    def test_upgrade_export_emits_flat_stack_and_preserves_source_state(self):
        (self.source / "staged-user-file").write_text("staged\n")
        self.git("add", "staged-user-file")
        (self.source / "working-user-file").write_text("working\n")
        (self.source / "value").write_text("unstaged user implementation\n")
        before = self.source_snapshot()
        output = self.root / "upgrade-flat"
        branch = "upgrade-flat-branch"

        result = STACK.export_upgrade(
            self.source, self.base, output, branch, root=self.root
        )

        self.assertEqual(result["status"], "upgrade-exported-source-verified")
        self.assertEqual(result["upstream_changed"], False)
        self.assertFalse(result["image_or_runtime_qualified"])
        self.assertEqual(result["patch_count"], 2)
        document, _ = self.assert_flat_stack(output, result)
        self.assertEqual(
            [entry["id"] for entry in document["patches"]], self.patch_ids()
        )
        self.assert_linear_patch_origins(document)
        self.assertEqual(self.git("rev-parse", branch), result["engine_commit"])
        self.assertEqual(self.source_snapshot(), before)
        self.assertEqual((self.source / "working-user-file").read_text(), "working\n")
        self.assertEqual((self.source / "staged-user-file").read_text(), "staged\n")
        self.assertEqual(
            (self.source / "value").read_text(), "unstaged user implementation\n"
        )

    def test_upgrade_export_preserves_unrelated_upstream_and_consumes_flat_stack(self):
        upstream_one = self.make_upstream_commit(self.base, "upstream-one", "one\n")
        output_one = self.root / "upgrade-one"
        result_one = STACK.export_upgrade(
            self.source, upstream_one, output_one, "upgrade-one-branch", root=self.root
        )
        repeat = STACK.export_upgrade(
            self.source,
            upstream_one,
            self.root / "upgrade-one-repeat",
            "upgrade-one-repeat-branch",
            root=self.root,
        )
        self.assertEqual(result_one["engine_tree"], repeat["engine_tree"])
        self.assertEqual(result_one["patch_count"], repeat["patch_count"])

        upstream_two = self.make_upstream_commit(upstream_one, "upstream-two", "two\n")
        output_two = self.root / "upgrade-two"
        result_two = STACK.export_upgrade(
            self.source,
            upstream_two,
            output_two,
            "upgrade-two-branch",
            root=output_one,
        )
        self.assertTrue(result_two["upstream_changed"])
        self.assertEqual(
            self.git("show", result_two["engine_tree"] + ":upstream-one"), "one"
        )
        self.assertEqual(
            self.git("show", result_two["engine_tree"] + ":upstream-two"), "two"
        )
        self.assertEqual(
            self.git("show", result_two["engine_tree"] + ":value"), "complete"
        )
        self.assert_flat_stack(output_two, result_two)

    def test_upgrade_export_rejects_output_inside_source_or_existing_output_branch(
        self,
    ):
        before = self.source_snapshot()
        with self.assertRaises(STACK.StackError):
            STACK.export_upgrade(
                self.source,
                self.base,
                self.source / "inside-source",
                "inside-source-branch",
                root=self.root,
            )
        self.assertFalse((self.source / "inside-source").exists())
        self.assertEqual(self.source_snapshot(), before)

        output = self.root / "already-there"
        output.mkdir()
        sentinel = output / "sentinel"
        sentinel.write_text("keep\n")
        with self.assertRaises(STACK.StackError):
            STACK.export_upgrade(
                self.source, self.base, output, "fresh-branch", root=self.root
            )
        self.assertEqual(sentinel.read_text(), "keep\n")
        self.assertFalse(self.git_ok("show-ref", "--verify", "refs/heads/fresh-branch"))

        existing_branch = "already-existing-branch"
        self.git("branch", existing_branch)
        fresh_output = self.root / "branch-rejected"
        with self.assertRaises(STACK.StackError):
            STACK.export_upgrade(
                self.source, self.base, fresh_output, existing_branch, root=self.root
            )
        self.assertFalse(fresh_output.exists())
        self.assertEqual(self.source_snapshot(), before)

    def test_upgrade_export_without_decision_rejects_conflict_or_already_present(self):
        already_present_output = self.root / "already-present"
        with self.assertRaises(STACK.StackError):
            STACK.export_upgrade(
                self.source,
                self.frozen,
                already_present_output,
                "already-present-branch",
                root=self.root,
            )
        self.assertFalse(already_present_output.exists())

        conflict = self.make_upstream_commit(self.base, "value", "conflict\n")
        conflict_output = self.root / "conflict"
        with self.assertRaises(STACK.StackError):
            STACK.export_upgrade(
                self.source,
                conflict,
                conflict_output,
                "conflict-branch",
                root=self.root,
            )
        self.assertFalse(conflict_output.exists())
        self.assertFalse(
            self.git_ok("show-ref", "--verify", "refs/heads/conflict-branch")
        )

    def test_upgrade_export_explicit_drop_requires_context_and_can_drop_only_named_patch(
        self,
    ):
        first_id, second_id = self.patch_ids()
        decisions = self.write_decisions(
            self.frozen,
            [
                {
                    "id": first_id,
                    "action": "drop",
                    "reason": "already present in the selected upstream commit",
                    "evidence": "fixture upstream tree equals the first patch result tree",
                }
            ],
        )
        output = self.root / "drop-one"
        result = STACK.export_upgrade(
            self.source,
            self.frozen,
            output,
            "drop-one-branch",
            decisions=decisions,
            root=self.root,
        )
        document, _ = self.assert_flat_stack(output, result)
        self.assertEqual([entry["id"] for entry in document["patches"]], [second_id])
        self.assertEqual(self.git("show", result["engine_tree"] + ":value"), "complete")

    def test_upgrade_export_replace_requires_exact_parent_tree_and_preserves_origin(
        self,
    ):
        first_id, _ = self.patch_ids()
        upstream = self.make_upstream_commit(
            self.base, "value", "upstream changed implementation\n"
        )
        replacement = self.make_replacement_commit(upstream)
        decisions = self.write_decisions(
            upstream,
            [
                {
                    "id": first_id,
                    "action": "replace",
                    "reason": "adapt the first patch to the changed upstream content",
                    "evidence": "replacement parent is the new upstream and its result restores the required first-patch contract",
                    "source_commit": replacement,
                }
            ],
        )
        output = self.root / "replace-good"
        result = STACK.export_upgrade(
            self.source,
            upstream,
            output,
            "replace-good-branch",
            decisions=decisions,
            root=self.root,
        )
        document, _ = self.assert_flat_stack(output, result)
        self.assertIn(replacement, json.dumps(document["reviewed_decisions"]))
        self.assertEqual(result["engine_tree"], self.tree(self.engine))

        wrong_parent = self.make_replacement_commit(self.frozen, "wrong parent")
        bad_decisions = self.write_decisions(
            upstream,
            [
                {
                    "id": first_id,
                    "action": "replace",
                    "reason": "wrong-parent fixture",
                    "evidence": "parent intentionally does not equal the cumulative tree",
                    "source_commit": wrong_parent,
                }
            ],
            name="bad-replace-decisions.json",
        )
        bad_output = self.root / "replace-bad"
        with self.assertRaises(STACK.StackError):
            STACK.export_upgrade(
                self.source,
                upstream,
                bad_output,
                "replace-bad-branch",
                decisions=bad_decisions,
                root=self.root,
            )
        self.assertFalse(bad_output.exists())
        merge = self.git(
            "commit-tree",
            self.tree(replacement),
            "-p",
            upstream,
            "-p",
            self.engine,
            "-m",
            "ambiguous merge replacement",
        )
        merge_decisions = self.write_decisions(
            upstream,
            [
                {
                    "id": first_id,
                    "action": "replace",
                    "source_commit": merge,
                    "reason": "merge rejection control",
                    "evidence": "two parent commits",
                }
            ],
            name="merge-replace-decisions.json",
        )
        with self.assertRaisesRegex(STACK.StackError, "single-parent"):
            STACK.export_upgrade(
                self.source,
                upstream,
                self.root / "merge-rejected",
                "merge-rejected",
                decisions=merge_decisions,
                root=self.root,
            )

    def test_upgrade_decisions_reject_stale_duplicate_and_unknown_ids(self):
        first_id, _ = self.patch_ids()
        cases = (
            (
                "stale",
                {"source_stack_sha256": "0" * 64, "patches": []},
            ),
            (
                "wrong-target",
                {
                    "source_stack_sha256": self.stack_sha(),
                    "target_upstream": self.engine,
                    "patches": [],
                },
            ),
            (
                "missing-rationale",
                {
                    "source_stack_sha256": self.stack_sha(),
                    "patches": [
                        {"id": first_id, "action": "drop", "reason": "", "evidence": ""}
                    ],
                },
            ),
            (
                "duplicate",
                {
                    "source_stack_sha256": self.stack_sha(),
                    "patches": [
                        {
                            "id": first_id,
                            "action": "drop",
                            "reason": "duplicate fixture decision",
                            "evidence": "duplicate must reject",
                        },
                        {
                            "id": first_id,
                            "action": "drop",
                            "reason": "duplicate fixture decision",
                            "evidence": "duplicate must reject",
                        },
                    ],
                },
            ),
            (
                "unknown",
                {
                    "source_stack_sha256": self.stack_sha(),
                    "patches": [
                        {
                            "id": "9999-unknown",
                            "action": "drop",
                            "reason": "unknown fixture decision",
                            "evidence": "unknown id must reject",
                        }
                    ],
                },
            ),
        )
        for name, overrides in cases:
            with self.subTest(name=name):
                decisions = {
                    "schema": "phala.sglang.upgrade-decisions.v1",
                    "source_stack_sha256": overrides["source_stack_sha256"],
                    "target_upstream": overrides.get("target_upstream", self.base),
                    "patches": overrides["patches"],
                }
                path = self.root / f"{name}-decisions.json"
                path.write_bytes(STACK.canonical(decisions))
                output = self.root / f"{name}-output"
                with self.assertRaises(STACK.StackError):
                    STACK.export_upgrade(
                        self.source,
                        self.base,
                        output,
                        f"{name}-branch",
                        decisions=path,
                        root=self.root,
                    )
                self.assertFalse(output.exists())
                self.assertFalse(
                    self.git_ok("show-ref", "--verify", f"refs/heads/{name}-branch")
                )

    def test_upgrade_export_copies_dependency_and_regression_inputs(self):
        dependency_patch = self.root / "dependency.patch"
        dependency_patch.write_bytes(b"dependency fixture\n")
        dependency = {
            "schema": "phala.external-source.v1",
            "native": {
                "version": "fixture",
                "patch": dependency_patch.name,
                "patch_sha256": STACK.sha256(dependency_patch.read_bytes()),
            },
        }
        (self.root / "external-dependencies.json").write_bytes(
            STACK.canonical(dependency)
        )
        regressions = {"suites": {"cpu": [{"name": "fixture", "path": "x.py"}]}}
        (self.root / "regressions.json").write_bytes(STACK.canonical(regressions))

        output = self.root / "copied-inputs"
        result = STACK.export_upgrade(
            self.source, self.base, output, "copied-inputs-branch", root=self.root
        )
        self.assertIn("exported_stack", result)
        self.assertEqual(
            (output / "external-dependencies.json").read_bytes(),
            (self.root / "external-dependencies.json").read_bytes(),
        )
        self.assertEqual(
            (output / "regressions.json").read_bytes(),
            (self.root / "regressions.json").read_bytes(),
        )
        self.assertEqual(
            (output / dependency_patch.name).read_bytes(), dependency_patch.read_bytes()
        )
        for entry in STACK.read_stack(output)["patches"]:
            self.assertTrue((output / entry["path"]).is_file())


if __name__ == "__main__":
    unittest.main()
