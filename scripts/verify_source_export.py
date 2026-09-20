#!/usr/bin/env python3
"""Verify source-backed SGLang patch exports without executing SGLang code.

The verifier deliberately accepts an already hydrated Git object database.  It
never fetches, checks out, builds, or imports the served source tree.  That
makes the proof usable both in CI and by a composed-image preparer, while
keeping network acquisition and later Governor composition separate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence


RESULT_SCHEMA = "phala.sglang-source-export-verification.v1"
MANIFEST_SCHEMA = "phala.sglang-serving-patches.v1"
PROFILE_SCHEMA = "phala.sglang-serving-profile.v1"
OBJECT_ID_RE = re.compile(r"[0-9a-f]{40,64}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
CANONICAL_DIFF_OPTIONS = (
    "--binary",
    "--full-index",
    "--no-ext-diff",
    "--no-textconv",
    "--no-color",
    "--no-renames",
    "--unified=3",
    "--diff-algorithm=myers",
    "--src-prefix=a/",
    "--dst-prefix=b/",
)


class VerificationError(RuntimeError):
    """A deterministic verification failure suitable for CI evidence."""

    def __init__(self, code: str, message: str, **details: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def as_dict(self) -> dict[str, Any]:
        record: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            record["details"] = self.details
        return record


class GitCommandError(RuntimeError):
    def __init__(self, args: Sequence[str], returncode: int, stderr: bytes) -> None:
        self.args = tuple(args)
        self.returncode = returncode
        self.stderr = stderr.decode("utf-8", errors="replace").strip()
        super().__init__(self.stderr or f"git exited {returncode}")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path, label: str) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise VerificationError(
            "input_unreadable", f"Cannot read {label}", path=str(path), reason=str(exc)
        ) from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(
            "input_not_json", f"{label} must be UTF-8 JSON (JSON is valid YAML)", path=str(path)
        ) from exc
    if not isinstance(value, dict):
        raise VerificationError("input_not_mapping", f"{label} must contain an object", path=str(path))
    return value, _sha256(raw)


def _mapping(value: Any, context: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError("metadata_invalid", f"{context} must be an object")
    return value


def _list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        raise VerificationError("metadata_invalid", f"{context} must be an array")
    return value


def _string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise VerificationError("metadata_invalid", f"{context} must be a non-empty string")
    return value


def _object_id(value: Any, context: str) -> str:
    object_id = _string(value, context)
    if not OBJECT_ID_RE.fullmatch(object_id):
        raise VerificationError("metadata_invalid", f"{context} must be a lowercase Git object ID")
    return object_id


def _sha256_value(value: Any, context: str) -> str:
    digest = _string(value, context)
    if not SHA256_RE.fullmatch(digest):
        raise VerificationError("metadata_invalid", f"{context} must be a lowercase SHA-256")
    return digest


def _safe_patch_path(patch_root: Path, raw_path: Any, context: str) -> Path:
    path_text = _string(raw_path, context)
    if path_text.startswith("/") or "\\" in path_text:
        raise VerificationError("patch_path_invalid", f"{context} must be a relative POSIX path")
    parts = path_text.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise VerificationError("patch_path_invalid", f"{context} escapes the patch root")
    root = patch_root.resolve()
    candidate = (root / path_text).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise VerificationError("patch_path_invalid", f"{context} escapes the patch root") from exc
    return candidate


def _git(
    source_repo: Path,
    args: Sequence[str],
    *,
    env: Mapping[str, str] | None = None,
    stdin: bytes | None = None,
) -> bytes:
    command = ["git", "-C", str(source_repo), *args]
    command_env = os.environ.copy()
    # Callers may themselves be inside another Git operation. Do not inherit
    # an alternate index, object database, work tree, or Git directory.
    for variable in (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_EXTERNAL_DIFF",
        "GIT_DIFF_OPTS",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_PARAMETERS",
    ):
        command_env.pop(variable, None)
    for variable in tuple(command_env):
        if variable.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")):
            command_env.pop(variable, None)
    # A partial/promisor clone must be hydrated before verification.  Do not
    # turn an offline proof into an unrecorded network fetch.
    command_env["GIT_NO_LAZY_FETCH"] = "1"
    command_env["GIT_TERMINAL_PROMPT"] = "0"
    if env:
        command_env.update(env)
    try:
        completed = subprocess.run(
            command,
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=command_env,
        )
    except OSError as exc:
        raise VerificationError("git_unavailable", "Cannot start Git", reason=str(exc)) from exc
    if completed.returncode:
        raise GitCommandError(command, completed.returncode, completed.stderr)
    return completed.stdout


def _missing_object(
    object_id: str,
    object_type: str,
    error: GitCommandError | None = None,
) -> VerificationError:
    details: dict[str, Any] = {"object": object_id, "object_type": object_type}
    if error and error.stderr:
        details["git_stderr"] = error.stderr
    return VerificationError(
        "missing_object",
        "Source Git objects are incomplete; hydrate the named immutable object before verification",
        **details,
    )


def _ensure_commit(source_repo: Path, commit: str) -> None:
    try:
        _git(source_repo, ["cat-file", "-e", f"{commit}^{{commit}}"])
    except GitCommandError as exc:
        raise _missing_object(commit, "commit", exc) from exc


def _ensure_tree(source_repo: Path, tree: str) -> None:
    try:
        _git(source_repo, ["cat-file", "-e", f"{tree}^{{tree}}"])
    except GitCommandError as exc:
        raise _missing_object(tree, "tree", exc) from exc


def _commit_parents(source_repo: Path, commit: str) -> list[str]:
    try:
        headers = _git(source_repo, ["cat-file", "commit", commit]).split(b"\n\n", 1)[0]
    except GitCommandError as exc:
        raise _missing_object(commit, "commit", exc) from exc
    parents: list[str] = []
    try:
        for line in headers.splitlines():
            if line.startswith(b"parent "):
                parent = line.removeprefix(b"parent ").decode("ascii")
                if not OBJECT_ID_RE.fullmatch(parent):
                    raise VerificationError("git_output_invalid", "Git returned an invalid commit parent ID")
                parents.append(parent)
    except UnicodeDecodeError as exc:
        raise VerificationError("git_output_invalid", "Git returned a non-ASCII commit parent list") from exc
    return parents


def _commit_tree(source_repo: Path, commit: str) -> str:
    try:
        tree = _git(source_repo, ["rev-parse", "--verify", f"{commit}^{{tree}}"]).decode(
            "ascii"
        ).strip()
    except (GitCommandError, UnicodeDecodeError) as exc:
        if isinstance(exc, GitCommandError):
            raise _missing_object(commit, "tree", exc) from exc
        raise VerificationError("git_output_invalid", "Git returned a non-ASCII tree ID") from exc
    if not OBJECT_ID_RE.fullmatch(tree):
        raise VerificationError("git_output_invalid", "Git returned an invalid tree ID", commit=commit)
    return tree


def _tree_blob_ids(source_repo: Path, tree: str) -> set[str]:
    try:
        listing = _git(source_repo, ["ls-tree", "-r", "-z", "--full-tree", tree])
    except GitCommandError as exc:
        raise _missing_object(tree, "tree", exc) from exc
    blob_ids: set[str] = set()
    for entry in listing.split(b"\0"):
        if not entry:
            continue
        try:
            metadata, _path = entry.split(b"\t", 1)
            mode, object_type, object_id = metadata.split(b" ", 2)
        except ValueError as exc:
            raise VerificationError("git_output_invalid", "Git returned an invalid tree entry", tree=tree) from exc
        if mode not in {b"100644", b"100755", b"120000"}:
            # A gitlink is represented in the tree itself; it has no source
            # blob in this repository to hydrate or read.
            if object_type == b"commit" and mode == b"160000":
                continue
            raise VerificationError("git_output_invalid", "Git returned an unsupported tree entry", tree=tree)
        if object_type != b"blob":
            raise VerificationError("git_output_invalid", "Git returned a non-blob file entry", tree=tree)
        decoded_id = object_id.decode("ascii")
        if not OBJECT_ID_RE.fullmatch(decoded_id):
            raise VerificationError("git_output_invalid", "Git returned an invalid blob ID", tree=tree)
        blob_ids.add(decoded_id)
    return blob_ids


def _ensure_complete_trees(source_repo: Path, trees: Iterable[str]) -> int:
    blob_ids: set[str] = set()
    for tree in sorted(set(trees)):
        _ensure_tree(source_repo, tree)
        blob_ids.update(_tree_blob_ids(source_repo, tree))
    if not blob_ids:
        return 0
    ordered_ids = sorted(blob_ids)
    try:
        output = _git(
            source_repo,
            ["cat-file", "--batch-check"],
            stdin=("\n".join(ordered_ids) + "\n").encode("ascii"),
        )
    except GitCommandError as exc:
        raise VerificationError(
            "missing_object",
            "Source Git objects are incomplete; hydrate required blobs before verification",
            git_stderr=exc.stderr,
        ) from exc
    lines = output.splitlines()
    if len(lines) != len(ordered_ids):
        raise VerificationError(
            "git_output_invalid",
            "Git returned an incomplete batch object response",
            expected=len(ordered_ids),
            got=len(lines),
        )
    missing: list[str] = []
    for object_id, line in zip(ordered_ids, lines, strict=True):
        fields = line.split()
        if len(fields) < 2 or fields[0].decode("ascii", errors="replace") != object_id:
            raise VerificationError("git_output_invalid", "Git returned a malformed batch object response")
        if fields[1] != b"blob":
            missing.append(object_id)
    if missing:
        raise VerificationError(
            "missing_object",
            "Source Git objects are incomplete; hydrate required blobs before verification",
            object_type="blob",
            missing=missing[:20],
            missing_count=len(missing),
        )
    return len(ordered_ids)


def _source_entries(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    entries: dict[str, Mapping[str, Any]] = {}
    groups: list[tuple[str, list[Any]]] = [("common", _list(manifest.get("common"), "manifest.common"))]
    models = _mapping(manifest.get("models"), "manifest.models")
    for name in sorted(models):
        groups.append((f"models.{name}", _list(models[name], f"manifest.models.{name}")))
    for group, values in groups:
        for index, value in enumerate(values):
            entry = _mapping(value, f"{group}[{index}]")
            patch_id = _string(entry.get("id"), f"{group}[{index}].id")
            if patch_id in entries:
                raise VerificationError("metadata_invalid", "Manifest has duplicate patch IDs", patch_id=patch_id)
            entries[patch_id] = entry
    return entries


def _dependencies(value: Any, context: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (_object_id(value, context),)
    if isinstance(value, list):
        return tuple(_object_id(item, f"{context}[{index}]") for index, item in enumerate(value))
    raise VerificationError("metadata_invalid", f"{context} must be null, a commit ID, or an array of commit IDs")


def _additional_patch_bindings(
    additional_patches: Sequence[tuple[str, bytes]], expected_composed_tree: str | None
) -> tuple[list[dict[str, Any]], str | None]:
    if isinstance(additional_patches, (bytes, bytearray, str)):
        raise VerificationError(
            "additional_patches_invalid", "additional_patches must be a sequence of (label, bytes) pairs"
        )
    bindings: list[dict[str, Any]] = []
    seen_labels: set[str] = set()
    for position, item in enumerate(additional_patches, start=1):
        if not isinstance(item, tuple) or len(item) != 2:
            raise VerificationError(
                "additional_patches_invalid", "Each additional patch must be a (label, bytes) tuple", position=position
            )
        label, patch_bytes = item
        label = _string(label, f"additional_patches[{position}].label")
        if any(character in label for character in "\r\n\0"):
            raise VerificationError(
                "additional_patches_invalid", "Additional patch labels must be single-line text", position=position
            )
        if label in seen_labels:
            raise VerificationError("additional_patches_invalid", "Additional patch labels must be unique", label=label)
        if not isinstance(patch_bytes, bytes) or not patch_bytes:
            raise VerificationError(
                "additional_patches_invalid", "Each additional patch must have non-empty raw bytes", label=label
            )
        bindings.append({"position": position, "label": label, "bytes": patch_bytes, "sha256": _sha256(patch_bytes)})
        seen_labels.add(label)
    if bindings:
        if expected_composed_tree is None:
            raise VerificationError(
                "expected_composed_tree_missing", "additional_patches requires an expected_composed_tree"
            )
        return bindings, _object_id(expected_composed_tree, "expected_composed_tree")
    if expected_composed_tree is not None:
        raise VerificationError(
            "additional_patches_missing", "expected_composed_tree is only valid when additional_patches are supplied"
        )
    return bindings, None


def _profile_bindings(
    manifest: Mapping[str, Any],
    profile: Mapping[str, Any],
    patch_root: Path,
) -> tuple[list[dict[str, Any]], str, Mapping[str, Any]]:
    manifest_entries = _source_entries(manifest)
    profile_patches = _list(profile.get("patches"), "profile.patches")
    if not profile_patches:
        raise VerificationError("metadata_invalid", "profile.patches must not be empty")
    bindings: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_commits: set[str] = set()
    for index, value in enumerate(profile_patches):
        profile_entry = _mapping(value, f"profile.patches[{index}]")
        patch_id = _string(profile_entry.get("id"), f"profile.patches[{index}].id")
        if patch_id in seen_ids:
            raise VerificationError(
                "duplicate_profile_patch", "Profile selects a patch more than once", patch_id=patch_id
            )
        try:
            manifest_entry = manifest_entries[patch_id]
        except KeyError as exc:
            raise VerificationError(
                "profile_patch_unknown", "Profile selects a patch absent from the manifest", patch_id=patch_id
            ) from exc
        manifest_path = _string(manifest_entry.get("path"), f"manifest[{patch_id}].path")
        profile_path = _string(profile_entry.get("path"), f"profile.patches[{index}].path")
        if profile_path != manifest_path:
            raise VerificationError(
                "profile_patch_mismatch",
                "Profile patch path does not match the manifest",
                patch_id=patch_id,
                profile_path=profile_path,
                manifest_path=manifest_path,
            )
        manifest_sha = _sha256_value(manifest_entry.get("sha256"), f"manifest[{patch_id}].sha256")
        profile_sha = _sha256_value(profile_entry.get("sha256"), f"profile.patches[{index}].sha256")
        if profile_sha != manifest_sha:
            raise VerificationError(
                "profile_patch_mismatch",
                "Profile patch SHA-256 does not match the manifest",
                patch_id=patch_id,
            )
        patch_path = _safe_patch_path(patch_root, manifest_path, f"manifest[{patch_id}].path")
        try:
            patch_bytes = patch_path.read_bytes()
        except OSError as exc:
            raise VerificationError(
                "patch_unreadable",
                "Cannot read selected patch",
                patch_id=patch_id,
                path=str(patch_path),
                reason=str(exc),
            ) from exc
        patch_sha = _sha256(patch_bytes)
        if patch_sha != manifest_sha:
            raise VerificationError(
                "patch_sha256_mismatch",
                "Selected patch bytes do not match the manifest SHA-256",
                patch_id=patch_id,
                expected=manifest_sha,
                actual=patch_sha,
            )
        source = _mapping(manifest_entry.get("source"), f"manifest[{patch_id}].source")
        source_commit = _object_id(source.get("commit"), f"manifest[{patch_id}].source.commit")
        if source_commit in seen_commits:
            raise VerificationError(
                "duplicate_source_commit", "Profile selects one source commit more than once", commit=source_commit
            )
        bindings.append(
            {
                "id": patch_id,
                "path": manifest_path,
                "patch_path": patch_path,
                "patch_bytes": patch_bytes,
                "patch_sha256": manifest_sha,
                "source": {
                    "repository": _string(source.get("repository"), f"manifest[{patch_id}].source.repository"),
                    "commit": source_commit,
                    "parent": _object_id(source.get("parent"), f"manifest[{patch_id}].source.parent"),
                    "tree": _object_id(source.get("tree"), f"manifest[{patch_id}].source.tree"),
                    "dependencies": _dependencies(
                        source.get("dependencies"), f"manifest[{patch_id}].source.dependencies"
                    ),
                    "review_pr": _string(source.get("review_pr"), f"manifest[{patch_id}].source.review_pr"),
                },
            }
        )
        seen_ids.add(patch_id)
        seen_commits.add(source_commit)
    expected_tree = _object_id(profile.get("expected_tree"), "profile.expected_tree")
    return bindings, expected_tree, manifest_entries


def _validate_profile_structure(
    manifest: Mapping[str, Any], profile: Mapping[str, Any], bindings: Sequence[Mapping[str, Any]]
) -> tuple[str, Mapping[str, Any]]:
    if _string(manifest.get("schema"), "manifest.schema") != MANIFEST_SCHEMA:
        raise VerificationError("schema_unsupported", "Unsupported patch manifest schema")
    if _string(profile.get("schema"), "profile.schema") != PROFILE_SCHEMA:
        raise VerificationError("schema_unsupported", "Unsupported profile schema")
    manifest_upstream = _mapping(manifest.get("upstream"), "manifest.upstream")
    profile_upstream = _mapping(profile.get("upstream"), "profile.upstream")
    upstream_commit = _object_id(manifest_upstream.get("commit"), "manifest.upstream.commit")
    for field in ("commit", "repository", "tag"):
        manifest_value = _string(manifest_upstream.get(field), f"manifest.upstream.{field}")
        profile_value = _string(profile_upstream.get(field), f"profile.upstream.{field}")
        if profile_value != manifest_value:
            raise VerificationError(
                "profile_upstream_mismatch",
                "Profile upstream does not match the manifest",
                field=field,
                profile=profile_value,
                manifest=manifest_value,
            )
    repositories = {binding["source"]["repository"] for binding in bindings}
    if len(repositories) != 1:
        raise VerificationError(
            "source_repository_mismatch",
            "One verifier invocation accepts patches from exactly one source Git repository",
            repositories=sorted(repositories),
        )
    commit_positions = {binding["source"]["commit"]: position for position, binding in enumerate(bindings)}
    for position, binding in enumerate(bindings):
        source = binding["source"]
        for dependency in source["dependencies"]:
            dependency_position = commit_positions.get(dependency)
            if dependency_position is None:
                raise VerificationError(
                    "dependency_not_selected",
                    "A selected patch has an explicit source dependency absent from the profile",
                    patch_id=binding["id"],
                    dependency=dependency,
                )
            if dependency_position >= position:
                raise VerificationError(
                    "dependency_out_of_order",
                    "Profile places an explicit source dependency after its dependent patch",
                    patch_id=binding["id"],
                    dependency=dependency,
                )
    return upstream_commit, manifest_upstream


def _verify_source_commits(
    source_repo: Path, upstream_commit: str, bindings: Sequence[Mapping[str, Any]]
) -> list[str]:
    _ensure_commit(source_repo, upstream_commit)
    upstream_tree = _commit_tree(source_repo, upstream_commit)
    trees = [upstream_tree]
    for binding in bindings:
        source = binding["source"]
        commit = source["commit"]
        _ensure_commit(source_repo, commit)
        _ensure_commit(source_repo, source["parent"])
        parent_tree = _commit_tree(source_repo, source["parent"])
        parents = _commit_parents(source_repo, commit)
        if parents != [source["parent"]]:
            raise VerificationError(
                "source_parent_mismatch",
                "Actual Git parent does not match the manifest",
                patch_id=binding["id"],
                commit=commit,
                expected_parent=source["parent"],
                actual_parents=parents,
            )
        actual_tree = _commit_tree(source_repo, commit)
        if actual_tree != source["tree"]:
            raise VerificationError(
                "source_tree_mismatch",
                "Actual source commit tree does not match the manifest",
                patch_id=binding["id"],
                commit=commit,
                expected_tree=source["tree"],
                actual_tree=actual_tree,
            )
        trees.append(actual_tree)
        # A source parent can be deliberately unselected in a non-linear
        # profile. Its full tree is still an input to the canonical diff.
        trees.append(parent_tree)
    return trees


def _canonical_diff(source_repo: Path, parent: str, commit: str) -> bytes:
    try:
        return _git(
            source_repo,
            [
                "-c",
                "core.quotePath=false",
                "diff",
                *CANONICAL_DIFF_OPTIONS,
                parent,
                commit,
                "--",
            ],
        )
    except GitCommandError as exc:
        raise VerificationError(
            "canonical_diff_unavailable",
            "Cannot regenerate the canonical Git diff from hydrated source objects",
            parent=parent,
            commit=commit,
            git_stderr=exc.stderr,
        ) from exc


def _source_object_directory(source_repo: Path) -> Path:
    try:
        common_dir_text = _git(source_repo, ["rev-parse", "--git-common-dir"]).decode("utf-8").strip()
    except (GitCommandError, UnicodeDecodeError) as exc:
        if isinstance(exc, GitCommandError):
            raise VerificationError(
                "git_repository_invalid", "Cannot resolve the source Git common directory", git_stderr=exc.stderr
            ) from exc
        raise VerificationError("git_repository_invalid", "Git returned a non-UTF-8 common directory") from exc
    common_dir = Path(common_dir_text)
    if not common_dir.is_absolute():
        common_dir = (source_repo / common_dir).resolve()
    object_directory = common_dir / "objects"
    if not object_directory.is_dir():
        raise VerificationError(
            "git_repository_invalid", "Source Git object directory does not exist", path=str(object_directory)
        )
    return object_directory


def _apply_profile_to_index(
    source_repo: Path,
    upstream_commit: str,
    bindings: Sequence[Mapping[str, Any]],
    expected_tree: str,
    additional_bindings: Sequence[Mapping[str, Any]],
    expected_composed_tree: str | None,
) -> tuple[str, str | None]:
    with tempfile.TemporaryDirectory(prefix="source-export-index-") as temporary_directory:
        temp_root = Path(temporary_directory)
        index_path = temp_root / "index"
        work_tree = temp_root / "work-tree"
        object_directory = temp_root / "objects"
        work_tree.mkdir()
        object_directory.mkdir()
        index_env = {
            "GIT_INDEX_FILE": str(index_path),
            "GIT_WORK_TREE": str(work_tree),
            # Read all immutable source objects through an alternate, but put
            # any transient index/apply tree objects in the temp directory.
            # This keeps the supplied source object database unchanged.
            "GIT_OBJECT_DIRECTORY": str(object_directory),
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(_source_object_directory(source_repo)),
        }
        try:
            _git(source_repo, ["-c", "core.autocrlf=false", "read-tree", upstream_commit], env=index_env)
        except GitCommandError as exc:
            raise VerificationError(
                "profile_patch_apply_failed",
                "Cannot initialize a separate Git index from the upstream commit",
                git_stderr=exc.stderr,
            ) from exc
        for binding in bindings:
            try:
                _git(
                    source_repo,
                    [
                        "-c",
                        "core.autocrlf=false",
                        "apply",
                        "--cached",
                        "--whitespace=nowarn",
                        str(binding["patch_path"]),
                    ],
                    env=index_env,
                )
            except GitCommandError as exc:
                raise VerificationError(
                    "profile_patch_apply_failed",
                    "A selected patch does not apply cleanly to a separate index from the upstream commit",
                    patch_id=binding["id"],
                    git_stderr=exc.stderr,
                ) from exc
        try:
            computed_tree = _git(source_repo, ["write-tree"], env=index_env).decode("ascii").strip()
        except (GitCommandError, UnicodeDecodeError) as exc:
            if isinstance(exc, GitCommandError):
                raise VerificationError(
                    "profile_patch_apply_failed", "Cannot write the pure-serving index tree", git_stderr=exc.stderr
                ) from exc
            raise VerificationError("git_output_invalid", "Git returned a non-ASCII computed tree ID") from exc
        if not OBJECT_ID_RE.fullmatch(computed_tree):
            raise VerificationError("git_output_invalid", "Git returned an invalid computed tree ID")
        if computed_tree != expected_tree:
            raise VerificationError(
                "profile_tree_mismatch",
                "Selected patches produced a full Git tree different from profile.expected_tree",
                expected_tree=expected_tree,
                computed_tree=computed_tree,
            )

        computed_composed_tree: str | None = None
        if additional_bindings:
            assert expected_composed_tree is not None
            for binding in additional_bindings:
                try:
                    _git(
                        source_repo,
                        ["-c", "core.autocrlf=false", "apply", "--cached", "--whitespace=nowarn", "-"],
                        env=index_env,
                        stdin=binding["bytes"],
                    )
                except GitCommandError as exc:
                    raise VerificationError(
                        "additional_patch_apply_failed",
                        "An additional patch does not apply cleanly after the verified pure-serving profile",
                        label=binding["label"],
                        sha256=binding["sha256"],
                        git_stderr=exc.stderr,
                    ) from exc
            try:
                computed_composed_tree = _git(source_repo, ["write-tree"], env=index_env).decode("ascii").strip()
            except (GitCommandError, UnicodeDecodeError) as exc:
                if isinstance(exc, GitCommandError):
                    raise VerificationError(
                        "additional_patch_apply_failed",
                        "Cannot write the additional-patch index tree",
                        git_stderr=exc.stderr,
                    ) from exc
                raise VerificationError("git_output_invalid", "Git returned a non-ASCII composed tree ID") from exc
            if not OBJECT_ID_RE.fullmatch(computed_composed_tree):
                raise VerificationError("git_output_invalid", "Git returned an invalid composed tree ID")
            if computed_composed_tree != expected_composed_tree:
                raise VerificationError(
                    "composed_tree_mismatch",
                    "Additional patch bytes produced a full Git tree different from expected_composed_tree",
                    expected_composed_tree=expected_composed_tree,
                    computed_composed_tree=computed_composed_tree,
                )
    return computed_tree, computed_composed_tree


def verify_source_export(
    source_repo: str | Path,
    manifest_path: str | Path,
    profile_path: str | Path,
    *,
    patch_root: str | Path | None = None,
    additional_patches: Sequence[tuple[str, bytes]] = (),
    expected_composed_tree: str | None = None,
) -> dict[str, Any]:
    """Return Git-only provenance evidence for one explicit serving profile.

    ``source_repo`` must already contain the upstream, selected source commits,
    their recorded parents, and all blobs in those input trees. This function
    does no network acquisition and does not evaluate source files.
    ``additional_patches`` may contain already
    validated component bytes, such as Governor hooks; their provenance is not
    checked here. Its success says nothing about PR approval, image
    qualification, or deployment acceptance.
    """

    source_path = Path(source_repo)
    manifest_file = Path(manifest_path)
    profile_file = Path(profile_path)
    root = Path(patch_root) if patch_root is not None else manifest_file.parent
    manifest, manifest_sha256 = _read_json(manifest_file, "manifest")
    profile, profile_sha256 = _read_json(profile_file, "profile")
    bindings, expected_tree, _manifest_entries = _profile_bindings(manifest, profile, root)
    additional_bindings, composed_tree_expected = _additional_patch_bindings(
        additional_patches, expected_composed_tree
    )
    upstream_commit, manifest_upstream = _validate_profile_structure(manifest, profile, bindings)
    source_trees = _verify_source_commits(source_path, upstream_commit, bindings)
    # expected_tree is a profile assertion, not necessarily a source commit
    # tree: a valid non-linear profile may produce a new composition. Only
    # hydrate and inspect the actual upstream/source trees needed as inputs.
    checked_blob_count = _ensure_complete_trees(source_path, source_trees)

    ordered_patches: list[dict[str, Any]] = []
    for position, binding in enumerate(bindings, start=1):
        source = binding["source"]
        canonical_bytes = _canonical_diff(source_path, source["parent"], source["commit"])
        canonical_sha256 = _sha256(canonical_bytes)
        if canonical_bytes != binding["patch_bytes"]:
            raise VerificationError(
                "canonical_diff_mismatch",
                "Patch bytes are not the canonical export of the recorded source commit",
                patch_id=binding["id"],
                patch_sha256=binding["patch_sha256"],
                canonical_diff_sha256=canonical_sha256,
            )
        ordered_patches.append(
            {
                "position": position,
                "id": binding["id"],
                "path": binding["path"],
                "patch_sha256": binding["patch_sha256"],
                "canonical_diff_sha256": canonical_sha256,
                "source": {
                    "repository": source["repository"],
                    "commit": source["commit"],
                    "parent": source["parent"],
                    "tree": source["tree"],
                    "dependencies": list(source["dependencies"]),
                    "review_pr": source["review_pr"],
                },
            }
        )

    computed_tree, computed_composed_tree = _apply_profile_to_index(
        source_path,
        upstream_commit,
        bindings,
        expected_tree,
        additional_bindings,
        composed_tree_expected,
    )

    return {
        "schema": RESULT_SCHEMA,
        "provenance_verified": True,
        "provenance_scope": "selected serving profile source commits and exported patch bytes",
        "review_approval": {
            "verified": False,
            "status": "not_checked",
            "reason": "Git export verification does not evaluate PR reviews or repository rules.",
        },
        "upstream": {
            "commit": upstream_commit,
            "repository": manifest_upstream["repository"],
            "tag": manifest_upstream["tag"],
        },
        "profile": {
            "id": _string(profile.get("id"), "profile.id"),
            "sha256": profile_sha256,
            "expected_tree": expected_tree,
        },
        "manifest": {
            "schema": manifest["schema"],
            "sha256": manifest_sha256,
        },
        "canonical_diff": {
            "arguments": [
                "git",
                "-c",
                "core.quotePath=false",
                "diff",
                *CANONICAL_DIFF_OPTIONS,
                "PARENT",
                "COMMIT",
                "--",
            ],
            "bytes_checked_against": "selected patch files",
        },
        "source_repository": bindings[0]["source"]["repository"],
        "ordered_patches": ordered_patches,
        "objects": {
            "complete_tree_blobs_checked": checked_blob_count,
            "lazy_fetch": "disabled",
        },
        "computed_tree": computed_tree,
        "expected_composed_tree": composed_tree_expected,
        "computed_composed_tree": computed_composed_tree,
        "additional_patches": [
            {
                "position": binding["position"],
                "label": binding["label"],
                "sha256": binding["sha256"],
                "provenance": "not_checked",
            }
            for binding in additional_bindings
        ],
    }


def _failure_record(error: VerificationError) -> dict[str, Any]:
    return {
        "schema": RESULT_SCHEMA,
        "provenance_verified": False,
        "provenance_scope": "selected serving profile source commits and exported patch bytes",
        "review_approval": {
            "verified": False,
            "status": "not_checked",
            "reason": "Git export verification does not evaluate PR reviews or repository rules.",
        },
        "error": error.as_dict(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-repo", required=True, type=Path, help="Hydrated local Git repository containing the source objects"
    )
    parser.add_argument("--manifest", required=True, type=Path, help="Versioned patch manifest JSON")
    parser.add_argument("--profile", required=True, type=Path, help="Explicit JSON-form YAML profile")
    parser.add_argument(
        "--patch-root",
        type=Path,
        help="Directory against which manifest patch paths resolve; defaults to the manifest directory",
    )
    arguments = parser.parse_args(argv)
    try:
        record = verify_source_export(
            arguments.source_repo,
            arguments.manifest,
            arguments.profile,
            patch_root=arguments.patch_root,
        )
    except VerificationError as exc:
        print(json.dumps(_failure_record(exc), indent=2, sort_keys=True))
        return 1
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
