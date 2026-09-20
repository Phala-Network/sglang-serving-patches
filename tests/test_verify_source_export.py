"""Behavioral coverage for the Git-only source-export verifier.

These tests construct a tiny complete Git history.  They exercise the proof
boundaries themselves; SGLang source is never imported or executed here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

from verify_source_export import CANONICAL_DIFF_OPTIONS, VerificationError, verify_source_export  # noqa: E402


def git(repository: Path, *arguments: str, stdin: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, indent=2) + "\n")


def write_text(path: Path, content: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write(content)


class SourceExportVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(prefix="source-export-test-")
        self.root = Path(self.temporary_directory.name)
        self.source = self.root / "source"
        self.patch_root = self.root / "patches"
        self.manifest_path = self.patch_root / "manifest.json"
        self.profile_path = self.root / "profile.yaml"
        self._create_source_history()
        self._write_metadata()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _create_source_history(self) -> None:
        subprocess.run(["git", "init", str(self.source)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git(self.source, "config", "user.name", "Verifier Test")
        git(self.source, "config", "user.email", "verifier@example.invalid")
        git(self.source, "config", "gc.auto", "0")
        write_text(self.source / "service.txt", "base\n")
        write_text(self.source / "unchanged.txt", "retained\n")
        git(self.source, "add", "service.txt", "unchanged.txt")
        git(self.source, "commit", "-m", "upstream base")
        self.upstream = git(self.source, "rev-parse", "HEAD").decode("ascii").strip()

        write_text(self.source / "service.txt", "first repair\n")
        git(self.source, "add", "service.txt")
        git(self.source, "commit", "-m", "first repair")
        self.first_commit = git(self.source, "rev-parse", "HEAD").decode("ascii").strip()

        write_text(self.source / "service.txt", "second repair\n")
        git(self.source, "add", "service.txt")
        git(self.source, "commit", "-m", "second repair")
        self.second_commit = git(self.source, "rev-parse", "HEAD").decode("ascii").strip()

        write_text(self.source / "governor-hook.txt", "optional hook\n")
        git(self.source, "add", "governor-hook.txt")
        git(self.source, "commit", "-m", "optional component hook")
        self.composed_commit = git(self.source, "rev-parse", "HEAD").decode("ascii").strip()

        git(self.source, "checkout", "-b", "nonlinear-parent", self.upstream)
        write_text(self.source / "parent-only.txt", "not selected\n")
        git(self.source, "add", "parent-only.txt")
        git(self.source, "commit", "-m", "unselected source parent")
        self.nonlinear_parent = git(self.source, "rev-parse", "HEAD").decode("ascii").strip()

        write_text(self.source / "service.txt", "standalone repair\n")
        git(self.source, "add", "service.txt")
        git(self.source, "commit", "-m", "standalone repair from unselected parent")
        self.nonlinear_child = git(self.source, "rev-parse", "HEAD").decode("ascii").strip()

        git(self.source, "checkout", "-b", "nonlinear-expected", self.upstream)
        write_text(self.source / "service.txt", "standalone repair\n")
        git(self.source, "add", "service.txt")
        git(self.source, "commit", "-m", "expected standalone profile tree")
        self.nonlinear_expected = git(self.source, "rev-parse", "HEAD").decode("ascii").strip()
        git(self.source, "checkout", "--detach", self.composed_commit)

    def _tree(self, commit: str) -> str:
        return git(self.source, "rev-parse", f"{commit}^{{tree}}").decode("ascii").strip()

    def _canonical_patch(self, parent: str, commit: str) -> bytes:
        return git(
            self.source,
            "-c",
            "core.quotePath=false",
            "diff",
            *CANONICAL_DIFF_OPTIONS,
            parent,
            commit,
            "--",
        )

    def _write_metadata(self) -> None:
        entries = []
        previous = self.upstream
        for index, commit in enumerate((self.first_commit, self.second_commit), start=1):
            patch_path = f"common/{index:04d}-repair.patch"
            patch = self._canonical_patch(previous, commit)
            target = self.patch_root / patch_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(patch)
            entries.append(
                {
                    "id": f"{index:04d}-repair",
                    "path": patch_path,
                    "sha256": hashlib.sha256(patch).hexdigest(),
                    "source": {
                        "repository": "https://github.com/example/source.git",
                        "commit": commit,
                        "parent": previous,
                        "tree": self._tree(commit),
                        "dependencies": None if index == 1 else self.first_commit,
                        "review_pr": f"https://github.com/example/source/pull/{index}",
                    },
                }
            )
            previous = commit
        manifest = {
            "schema": "phala.sglang-serving-patches.v1",
            "upstream": {
                "commit": self.upstream,
                "repository": "https://github.com/example/upstream.git",
                "tag": "v-test",
            },
            "common": entries,
            "models": {},
        }
        profile = {
            "schema": "phala.sglang-serving-profile.v1",
            "id": "test-profile",
            "upstream": manifest["upstream"],
            "expected_tree": self._tree(self.second_commit),
            "patches": [
                {"id": entry["id"], "path": entry["path"], "sha256": entry["sha256"]}
                for entry in entries
            ],
        }
        write_json(self.manifest_path, manifest)
        write_json(self.profile_path, profile)

    def _write_nonlinear_metadata(self) -> tuple[Path, Path]:
        patch_root = self.root / "nonlinear-patches"
        manifest_path = patch_root / "manifest.json"
        profile_path = self.root / "nonlinear-profile.yaml"
        patch = self._canonical_patch(self.nonlinear_parent, self.nonlinear_child)
        patch_path = patch_root / "common/0001-standalone.patch"
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        patch_path.write_bytes(patch)
        manifest = {
            "schema": "phala.sglang-serving-patches.v1",
            "upstream": {
                "commit": self.upstream,
                "repository": "https://github.com/example/upstream.git",
                "tag": "v-test",
            },
            "common": [
                {
                    "id": "0001-standalone",
                    "path": "common/0001-standalone.patch",
                    "sha256": hashlib.sha256(patch).hexdigest(),
                    "source": {
                        "repository": "https://github.com/example/source.git",
                        "commit": self.nonlinear_child,
                        "parent": self.nonlinear_parent,
                        "tree": self._tree(self.nonlinear_child),
                        "dependencies": None,
                        "review_pr": "https://github.com/example/source/pull/standalone",
                    },
                }
            ],
            "models": {},
        }
        profile = {
            "schema": "phala.sglang-serving-profile.v1",
            "id": "nonlinear-profile",
            "upstream": manifest["upstream"],
            "expected_tree": self._tree(self.nonlinear_expected),
            "patches": [
                {
                    "id": "0001-standalone",
                    "path": "common/0001-standalone.patch",
                    "sha256": manifest["common"][0]["sha256"],
                }
            ],
        }
        write_json(manifest_path, manifest)
        write_json(profile_path, profile)
        return manifest_path, profile_path

    def _read_manifest(self) -> dict[str, object]:
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def _read_profile(self) -> dict[str, object]:
        return json.loads(self.profile_path.read_text(encoding="utf-8"))

    def _source_object_inventory(self) -> list[str]:
        objects = self.source / ".git" / "objects"
        return sorted(str(path.relative_to(objects)) for path in objects.rglob("*") if path.is_file())

    def _assert_failure(self, code: str) -> None:
        with self.assertRaises(VerificationError) as raised:
            verify_source_export(self.source, self.manifest_path, self.profile_path)
        self.assertEqual(code, raised.exception.code)

    def test_verifies_canonical_exports_and_full_profile_tree(self) -> None:
        before_objects = self._source_object_inventory()
        record = verify_source_export(self.source, self.manifest_path, self.profile_path)

        self.assertTrue(record["provenance_verified"])
        self.assertEqual(self._tree(self.second_commit), record["computed_tree"])
        self.assertEqual(2, len(record["ordered_patches"]))
        self.assertFalse(record["review_approval"]["verified"])
        self.assertEqual("not_checked", record["review_approval"]["status"])
        self.assertEqual(before_objects, self._source_object_inventory())

    def test_allows_a_source_parent_that_is_not_selected_when_dependencies_are_explicit(self) -> None:
        manifest_path, profile_path = self._write_nonlinear_metadata()

        record = verify_source_export(self.source, manifest_path, profile_path)

        self.assertEqual(self._tree(self.nonlinear_expected), record["computed_tree"])
        self.assertEqual(self.nonlinear_parent, record["ordered_patches"][0]["source"]["parent"])

    def test_rejects_tampered_patch_bytes(self) -> None:
        patch_path = self.patch_root / "common/0001-repair.patch"
        patch_path.write_bytes(patch_path.read_bytes() + b"\n# tampered\n")

        self._assert_failure("patch_sha256_mismatch")

    def test_rejects_profile_order_that_places_explicit_dependency_after_dependent(self) -> None:
        profile = self._read_profile()
        patches = profile["patches"]
        assert isinstance(patches, list)
        profile["patches"] = [patches[1], patches[0]]
        write_json(self.profile_path, profile)

        self._assert_failure("dependency_out_of_order")

    def test_rejects_missing_explicit_dependency(self) -> None:
        manifest = self._read_manifest()
        common = manifest["common"]
        assert isinstance(common, list)
        source = common[1]["source"]
        assert isinstance(source, dict)
        source["dependencies"] = "f" * 40
        write_json(self.manifest_path, manifest)

        self._assert_failure("dependency_not_selected")

    def test_rejects_wrong_expected_end_tree(self) -> None:
        profile = self._read_profile()
        profile["expected_tree"] = self._tree(self.upstream)
        write_json(self.profile_path, profile)

        self._assert_failure("profile_tree_mismatch")

    def test_applies_additional_component_bytes_after_pure_profile(self) -> None:
        additional_patch = self._canonical_patch(self.second_commit, self.composed_commit)
        before_objects = self._source_object_inventory()
        record = verify_source_export(
            self.source,
            self.manifest_path,
            self.profile_path,
            additional_patches=(("governor-hook", additional_patch),),
            expected_composed_tree=self._tree(self.composed_commit),
        )

        self.assertEqual(self._tree(self.second_commit), record["computed_tree"])
        self.assertEqual(self._tree(self.composed_commit), record["computed_composed_tree"])
        self.assertEqual("not_checked", record["additional_patches"][0]["provenance"])
        self.assertEqual(before_objects, self._source_object_inventory())

    def test_rejects_wrong_composed_end_tree(self) -> None:
        additional_patch = self._canonical_patch(self.second_commit, self.composed_commit)

        with self.assertRaises(VerificationError) as raised:
            verify_source_export(
                self.source,
                self.manifest_path,
                self.profile_path,
                additional_patches=(("governor-hook", additional_patch),),
                expected_composed_tree=self._tree(self.upstream),
            )
        self.assertEqual("composed_tree_mismatch", raised.exception.code)

    def test_rejects_partial_clone_style_missing_blob(self) -> None:
        blob = git(self.source, "rev-parse", f"{self.upstream}:unchanged.txt").decode("ascii").strip()
        object_path = self.source / ".git" / "objects" / blob[:2] / blob[2:]
        self.assertTrue(object_path.is_file())
        object_path.unlink()

        self._assert_failure("missing_object")


if __name__ == "__main__":
    unittest.main()
