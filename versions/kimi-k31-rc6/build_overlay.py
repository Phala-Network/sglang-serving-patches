"""Build/check a small rc6 OCI/catalog/boot delta; no daemon, registry or VM calls.

The fixed vendor inputs, stock init template and boot tool are explicit CLI paths.
It never opens an app compose or an opaque startup field.
Non-K3 L0 records pass through as raw tar records without per-file extraction.
"""
from __future__ import annotations

import argparse
import base64
import copy
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tarfile
import zlib

VERSION = Path(__file__).resolve().parent
COMMIT = "bfe9d8575ca5b7e4698da844e3f9c0a36c392c9d"
BASE_CONFIG = "c25cf0896e0a94ec544500e4b05bb6b62b14ad294a9df17a0fb8124b21e6b57b"
BASE_MANIFEST = "e5ece94b04b0557639a05790aaf607bb0a55848b34fe63e334e4dcbeeafd55f3"
BASE_CATALOG = "b9a56b70c90d61606de0e5ada35c287ce0d114e65417bd93282d821fd4ee725c"
BASE_L0 = "0328daa8738a12899bc30019abbf264be75dab1f8509b6860d8df9204df3153f"
BASE_RELEASE = "12f1b457b74d40571f27d76bd0afe75dcab7fb417c27ada2941ada60da67ed04"
INIT_TEMPLATE = "e85a252014647c207a29daee35710756a779e3f4f909aa350a0cdf48d2196680"
BOOT_TOOL = "36cab9fe857807929782111610d683685bb04aef0250d92efa96703d8ce94d31"
ORIGINAL_SOURCE = "77ca1dda1ec1b29464bc0ed7b941123e2d5dc31e76c11be533505ba1caa1ea03"
PATCH = "68f03eae4ed03b0c0c49de2e2dee56d684f98d063735ac09fca7fd6d5ec848f7"
PATCHED_SOURCE = "a876ad5f36aad52a1c3ae71667a11e1f554022bbc43e7ba9fe26219058793baf"
SOURCE_PATH = "sgl-workspace/sglang/python/sglang/srt/multimodal/processors/kimi_k3.py"
LAYER_TYPE = "application/vnd.oci.image.layer.v1.tar"
CONFIG_TYPE = "application/vnd.oci.image.config.v1+json"
MANIFEST_TYPE = "application/vnd.oci.image.manifest.v1+json"
BASE_REF = "offline.invalid/ccimage/k3@sha256:" + BASE_MANIFEST
MARKER = b"@L0_BASE64@"


class GateError(Exception):
    pass


def require(ok, code):
    if not ok:
        raise GateError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def pretty(value):
    return json.dumps(value, sort_keys=True, indent=2).encode() + b"\n"


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def fixed(path, digest, code):
    raw = path.read_bytes()
    require(sha(raw) == digest, code)
    return raw


def layer_bytes(source):
    files = source if isinstance(source, dict) else {SOURCE_PATH: source}
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w", format=tarfile.GNU_FORMAT) as tar:
        for name, data in sorted(files.items()):
            info = tarfile.TarInfo(name)
            info.size, info.mode = len(data), 0o644
            info.uid = info.gid = info.mtime = 0
            tar.addfile(info, io.BytesIO(data))
    return out.getvalue()


def apply_runtime_patch(files, raw):
    """Apply exact LF hunks to selected runtime files; tests stay in source only."""
    text = re.sub(r"(?m)^(?:diff --git |index )[^\n]*\n", "", raw.decode("utf-8"))
    sections = re.split(r"(?m)(?=^--- a/)", text)[1:]
    require(sections, "stack_patch_no_sections")
    for section in sections:
        lines = section.splitlines(keepends=True)
        old_path = re.fullmatch(r"--- a/(\S+)\n", lines[0])
        new_path = re.fullmatch(r"\+\+\+ b/(\S+)\n", lines[1])
        require(old_path and new_path and old_path[1] == new_path[1], "stack_patch_paths")
        name = old_path[1]
        require(not name.startswith("/") and ".." not in Path(name).parts, "stack_patch_path_escape")
        if name.startswith("test/"):
            continue
        require(name in files, "stack_patch_unexpected_runtime_file")
        old = files[name].decode("utf-8").splitlines(keepends=True)
        result, cursor, index = [], 0, 2
        while index < len(lines):
            line = lines[index]
            if not line.startswith("@@ "):
                require(line.startswith(("index ", "--- a/", "+++ b/")), "stack_patch_header")
                index += 1
                continue
            match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            require(match is not None, "stack_patch_hunk")
            start = int(match[1]) - 1
            require(cursor <= start <= len(old), "stack_patch_hunk_order")
            result.extend(old[cursor:start])
            cursor = start
            old_count = new_count = 0
            index += 1
            while index < len(lines) and not lines[index].startswith("@@ "):
                change = lines[index]
                require(change[:1] in (" ", "+", "-"), "stack_patch_hunk_line")
                if change[:1] in (" ", "-"):
                    require(cursor < len(old) and old[cursor] == change[1:], "stack_patch_context")
                    cursor += 1
                    old_count += 1
                if change[:1] in (" ", "+"):
                    result.append(change[1:])
                    new_count += 1
                index += 1
            require(old_count == int(match[2] or 1) and new_count == int(match[4] or 1), "stack_patch_hunk_count")
        result.extend(old[cursor:])
        files[name] = "".join(result).encode("utf-8")


def legacy_overlay():
    return {"original_sha256": ORIGINAL_SOURCE, "patched_sha256": PATCHED_SOURCE, "patch_sha256": PATCH,
            "image_path": "/" + SOURCE_PATH, "complete_engine_source_commit": None,
            "source_boundary": "fixed rc6 OCI plus one file; complete engine provenance is unresolved"}


def runtime_stack(a):
    if a.stack == "mixed1":
        return None
    source_record = json.loads((VERSION / "source.json").read_bytes())
    raw = fixed(VERSION / "runtime2.json", source_record["runtime2"]["manifest_sha256"], "stack_manifest")
    spec = json.loads(raw)
    require(spec["schema"] == "phala-rc6-overlay-stack-v1" and spec["name"] == "runtime2", "stack_schema")
    require(spec["base_image_ref"] == BASE_REF, "stack_base")
    files = {}
    for row in spec["files"]:
        name = row["runtime_file"]
        require(name.startswith("python/sglang/srt/") and ".." not in Path(name).parts and name not in files, "stack_file_path")
        require(row["archive_path"] == "sgl-workspace/sglang/" + name, "stack_archive_path")
        fixture = VERSION / row["fixture"]
        require(fixture.resolve().is_relative_to(VERSION.resolve()), "stack_fixture_path")
        files[name] = fixed(fixture, row["original_sha256"], "stack_original_source")
    for row in spec["patches"]:
        path = VERSION / row["path"]
        require(path.resolve().is_relative_to(VERSION.resolve()), "stack_patch_path")
        apply_runtime_patch(files, fixed(path, row["sha256"], "stack_patch"))
    payloads = {}
    for row in spec["files"]:
        data = files[row["runtime_file"]]
        require(sha(data) == row["patched_sha256"], "stack_patched_source")
        payloads[row["archive_path"]] = data
    require(any(row["sha256"] == PATCH for row in spec["patches"]), "stack_mixed_patch_missing")
    require(sha(payloads[SOURCE_PATH]) == PATCHED_SOURCE, "stack_mixed_source_changed")
    overlay = legacy_overlay()
    overlay.update({"stack": "runtime2", "stack_manifest_sha256": sha(raw), "patches": spec["patches"],
                    "files": spec["files"], "source_boundary": "fixed rc6 OCI plus selected runtime files; complete engine provenance is unresolved"})
    return {"payloads": payloads, "overlay": overlay, "sha256": sha(raw)}


def tar_records(raw):
    """Read tar headers only; retain each nonselected record as opaque bytes."""
    records, offset, pending = {}, 0, None
    while offset + 512 <= len(raw):
        header = raw[offset:offset + 512]
        if header == bytes(512):
            require(pending is None, "tar_dangling_longname")
            require(raw[offset:] == bytes(len(raw) - offset), "tar_trailing_data")
            return records
        kind = header[156:157]
        require(kind in (b"0", b"\x00", b"5", b"L"), "unsupported_tar_record")
        checksum = int(header[148:156].strip(b" \x00") or b"0", 8)
        require(sum(header[:148] + b" " * 8 + header[156:]) == checksum, "tar_checksum")
        require(not header[345:500].strip(b"\x00"), "tar_prefix_not_supported")
        size = int(header[124:136].strip(b" \x00") or b"0", 8)
        end = offset + 512 + ((size + 511) // 512) * 512
        require(end <= len(raw), "truncated_tar_record")
        if kind == b"L":
            require(pending is None and size < 4096, "tar_longname")
            # GNU long-name payload is path metadata, not a file's content.
            name = raw[offset + 512:offset + 512 + size].rstrip(b"\x00").decode("utf-8")
            pending = (name, raw[offset:end])
            offset = end
            continue
        name = pending[0] if pending else header[:100].split(b"\x00", 1)[0].decode("utf-8")
        require(name and not name.startswith("/") and ".." not in Path(name).parts, "tar_path")
        require(name not in records, "duplicate_tar_path")
        records[name] = (pending[1] if pending else b"") + raw[offset:end]
        pending = None
        offset = end
    raise GateError("tar_end_missing")


def new_record(name, data):
    info = tarfile.TarInfo(name)
    info.size, info.mode = len(data), 0o644
    return info.tobuf(tarfile.GNU_FORMAT) + data + bytes(-len(data) % 512)


def new_l0(old_gzip, ref, manifest, config):
    records = tar_records(gzip.decompress(old_gzip))
    prefix = "images/k3/blobs/sha256/"
    old_blobs = {name for name in records if name.startswith(prefix) and not name.endswith("/")}
    require(old_blobs == {prefix + BASE_MANIFEST, prefix + BASE_CONFIG}, "base_k3_metadata_set")
    require("images/k3/ref" in records and "images/k3/source" in records, "base_k3_ref_missing")
    for name in old_blobs:
        del records[name]
    replacements = {
        "images/k3/ref": ref.encode() + b"\n",
        "images/k3/source": ref.encode() + b"\n",
        prefix + sha(manifest): manifest,
        prefix + sha(config): config,
    }
    for name, data in replacements.items():
        records[name] = new_record(name, data)
    tar = b"".join(records[name] for name in sorted(records)) + bytes(1024)
    tar += bytes(-len(tar) % 10240)
    out = io.BytesIO()
    with gzip.GzipFile(filename="", fileobj=out, mode="wb", compresslevel=9, mtime=0) as gz:
        gz.write(tar)
    return out.getvalue(), len(records)


def boot_image(init):
    # Match the pinned boot-volume.py's build() transport.
    compressed = gzip.compress(init, mtime=0)
    image = compressed + bytes(-len(compressed) % 4096)
    require(len(image) <= 64 << 20, "boot_volume_too_large")
    return image


def inputs(a):
    fixed(a.init_template, INIT_TEMPLATE, "fixed_init_template")
    fixed(a.boot_tool, BOOT_TOOL, "fixed_boot_tool")
    paths = {
        "config": (a.inputs / "rc6-k3-config.json", BASE_CONFIG),
        "manifest": (a.inputs / "rc6-k3-manifest.json", BASE_MANIFEST),
        "images": (a.inputs / "rc6-images.json", BASE_CATALOG),
        "l0": (a.inputs / "rc6-l0.tar.gz", BASE_L0),
        "release": (a.inputs / "rc6-release.json", BASE_RELEASE),
    }
    raw = {name: fixed(path, digest, "input_" + name) for name, (path, digest) in paths.items()}
    manifest, config, images, release = [json.loads(raw[n]) for n in ("manifest", "config", "images", "release")]
    require(manifest["layers"] == images["k3"]["layers"], "base_layer_descriptors")
    require(config["rootfs"]["diff_ids"] == [v["digest"] for v in manifest["layers"]], "base_diff_ids")
    require(len(manifest["layers"]) == 85 and images["k3"]["ref"] == BASE_REF, "base_identity")
    require(manifest["config"] == {"mediaType": CONFIG_TYPE, "digest": "sha256:" + BASE_CONFIG,
                                   "size": len(raw["config"])}, "base_config_descriptor")
    require(canonical(manifest) == raw["manifest"], "base_canonical_manifest")
    require(config["architecture"] == "amd64" and config["os"] == "linux", "base_platform")
    require(release["commit"] == COMMIT and release["images_sha256"] == BASE_CATALOG, "base_release")
    return raw, manifest, config, images, release


def check(out, a):
    raw, old_m, old_c, old_images, old_release = inputs(a)
    stack = runtime_stack(a)
    receipt = json.loads((out / "candidate.json").read_bytes())
    require(receipt["source_overlay"]["patch_sha256"] == PATCH, "receipt_patch")
    require(receipt["source_overlay"] == (stack["overlay"] if stack else legacy_overlay()), "receipt_source_overlay")
    require(receipt["prelaunch_field_accessed"] is False, "unexpected_startup_field_access")
    mhex, chex, lhex = [receipt[k].removeprefix("sha256:") for k in ("manifest_digest", "config_digest", "layer_digest")]
    blobs = out / "oci-delta/blobs/sha256"
    manifest = fixed(blobs / mhex, mhex, "candidate_manifest_digest")
    config = fixed(blobs / chex, chex, "candidate_config_digest")
    layer = fixed(blobs / lhex, lhex, "candidate_layer_digest")
    m, c = json.loads(manifest), json.loads(config)
    require(m["layers"][:-1] == old_m["layers"] and len(m["layers"]) == 86, "candidate_layer_prefix")
    require(m["layers"][-1] == {"mediaType": LAYER_TYPE, "digest": "sha256:" + lhex, "size": len(layer)}, "overlay_descriptor")
    require(m["config"] == {"mediaType": CONFIG_TYPE, "digest": "sha256:" + chex, "size": len(config)}, "candidate_config_descriptor")
    require(canonical(m) == manifest and canonical(c) == config, "candidate_canonical_json")
    require(c["rootfs"]["diff_ids"] == old_c["rootfs"]["diff_ids"] + ["sha256:" + lhex], "candidate_diff_ids")
    require(c["history"][:-1] == old_c["history"] and not c["history"][-1].get("empty_layer"), "candidate_history")
    history = "CCBridge immutable source overlay " + ("stack sha256:" + stack["sha256"] if stack else "sha256:" + PATCH)
    require(c["history"][-1] == {"created_by": history}, "candidate_history_entry")
    normalized = copy.deepcopy(c)
    normalized["rootfs"]["diff_ids"] = old_c["rootfs"]["diff_ids"]
    normalized["history"] = old_c["history"]
    require(normalized == old_c, "base_config_semantics_changed")
    with tarfile.open(fileobj=io.BytesIO(layer), mode="r:") as tar:
        members = tar.getmembers()
        expected = stack["payloads"] if stack else {SOURCE_PATH: None}
        require([m.name for m in members] == sorted(expected) and all(m.isfile() for m in members), "overlay_file_set")
        actual = {}
        for member in members:
            require((member.uid, member.gid, member.mtime, member.mode) == (0, 0, 0, 0o644), "overlay_file_metadata")
            data = tar.extractfile(member).read()
            digest = sha(expected[member.name]) if stack else PATCHED_SOURCE
            require(sha(data) == digest, "overlay_source_digest")
            actual[member.name] = data
        require(layer_bytes(actual) == layer, "overlay_tar_determinism")
    images_raw = (out / "catalog-delta/images.json").read_bytes()
    require(sha(images_raw) == receipt["images_sha256"], "catalog_digest")
    images = json.loads(images_raw)
    require({k: v for k, v in images.items() if k != "k3"} == {k: v for k, v in old_images.items() if k != "k3"}, "non_k3_catalog_changed")
    require(images["k3"] == {"ref": receipt["image_ref"], "config_digest": "sha256:" + chex, "layers": m["layers"]}, "catalog_k3")
    require((out / "catalog-delta/new-layers/sha256" / lhex).read_bytes() == layer, "catalog_layer")
    expected_l0, records = new_l0(raw["l0"], receipt["image_ref"], manifest, config)
    require((out / "l0.tar.gz").read_bytes() == expected_l0, "l0_metadata_repack")
    template = a.init_template.read_bytes()
    require(template.split(b"\n").count(MARKER) == 1, "init_template_marker")
    expected_init = template.replace(MARKER, base64.b64encode(expected_l0))
    init = (out / "init_script").read_bytes()
    require(init == expected_init, "init_script_metadata")
    boot = json.loads((out / "boot/boot-volume.json").read_bytes())
    image = fixed(out / "boot" / boot["image"], boot["sha256"], "boot_digest")
    require(image == boot_image(init) and gzip.decompress(image) == init and len(image) % 4096 == 0, "boot_transport")
    loader = (out / "boot/init_script").read_text()
    require(boot["sha256"] in loader and BASE_L0 not in loader, "boot_loader_pin")
    annotations = json.loads((out / "boot/annotations.json").read_bytes())
    require(annotations == {"ccbridge.boot_volume": boot["sha256"]}, "boot_annotation")
    delta = json.loads((out / "release.delta.json").read_bytes())
    require(delta["base_commit"] == COMMIT and delta["l1"] == old_release["l1"], "native_l1_changed")
    require(delta["new_layers"] == 1 and delta["images_sha256"] == receipt["images_sha256"], "release_delta")
    return {"passed": True, "image_ref": receipt["image_ref"], "config_digest": "sha256:" + chex,
            "layers": 86, "new_layers": 1, "new_layer_bytes": len(layer), "images_sha256": receipt["images_sha256"],
            "boot_volume_sha256": boot["sha256"], "boot_volume_bytes": len(image), "l0_records": records,
            "base_config_semantics_preserved": True, "non_k3_catalog_preserved": True,
            "overlay_files": len(actual), "stack": a.stack,
            "prelaunch_field_accessed": False, "final_runtime_executed": False,
            "source_publication_verified": False, "gpu_qualified": False}


def build(a):
    raw, old_m, old_c, old_images, old_release = inputs(a)
    stack = runtime_stack(a)
    if stack:
        source, overlay = stack["payloads"], stack["overlay"]
    else:
        source = fixed(a.patched_source, PATCHED_SOURCE, "patched_source")
        fixed(a.original_source, ORIGINAL_SOURCE, "original_source")
        fixed(a.patch, PATCH, "source_patch")
        overlay = legacy_overlay()
    layer = layer_bytes(source)
    lhex = sha(layer)
    config = copy.deepcopy(old_c)
    config["rootfs"]["diff_ids"].append("sha256:" + lhex)
    history = "CCBridge immutable source overlay " + ("stack sha256:" + stack["sha256"] if stack else "sha256:" + PATCH)
    config.setdefault("history", []).append({"created_by": history})
    config_bytes = canonical(config)
    chex = sha(config_bytes)
    layers = old_m["layers"] + [{"mediaType": LAYER_TYPE, "digest": "sha256:" + lhex, "size": len(layer)}]
    manifest = canonical({"schemaVersion": 2, "mediaType": MANIFEST_TYPE,
                          "config": {"mediaType": CONFIG_TYPE, "digest": "sha256:" + chex, "size": len(config_bytes)},
                          "layers": layers})
    mhex = sha(manifest)
    ref = "offline.invalid/ccimage/k3@sha256:" + mhex
    images = copy.deepcopy(old_images)
    images["k3"] = {"ref": ref, "config_digest": "sha256:" + chex, "layers": layers}
    images_bytes = pretty(images)
    catalog = sha(images_bytes)
    l0, records = new_l0(raw["l0"], ref, manifest, config_bytes)
    template = a.init_template.read_bytes()
    require(template.split(b"\n").count(MARKER) == 1, "init_template_marker")
    init = template.replace(MARKER, base64.b64encode(l0))
    require(len(base64.b64encode(l0)) <= 10 << 20, "l0_size_cap")
    a.out.mkdir(parents=True, exist_ok=False)
    blobs = a.out / "oci-delta/blobs/sha256"
    for digest, data in ((mhex, manifest), (chex, config_bytes), (lhex, layer)):
        write(blobs / digest, data)
    write(a.out / "oci-delta/oci-layout", b'{"imageLayoutVersion":"1.0.0"}\n')
    write(a.out / "oci-delta/index.json", pretty({"schemaVersion": 2, "manifests": [
        {"mediaType": MANIFEST_TYPE, "digest": "sha256:" + mhex, "size": len(manifest),
         "platform": {"architecture": "amd64", "os": "linux"},
         "annotations": {"org.opencontainers.image.ref.name": ref}}]}))
    write(a.out / "catalog-delta/images.json", images_bytes)
    write(a.out / "catalog-delta/new-layers/sha256" / lhex, layer)
    write(a.out / "l0.tar.gz", l0)
    write(a.out / "init_script", init)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    process = subprocess.run([sys.executable, str(a.boot_tool), "--init-script", str(a.out / "init_script"),
                              "--out", str(a.out / "boot")], capture_output=True, text=True, env=env)
    require(process.returncode == 0, "boot_volume_tool_failed")
    # The Linux recipe's text byte count is LF. Windows text I/O adds CRLF;
    # normalize only these newly generated transport files, never an app field.
    for name in ("init_script", "annotations.json", "boot-volume.json"):
        path = a.out / "boot" / name
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    boot = json.loads((a.out / "boot/boot-volume.json").read_bytes())
    known = {row["digest"] for value in old_images.values() for row in value["layers"]}
    receipt = {"base_commit": COMMIT, "base_image_ref": BASE_REF, "base_config_digest": "sha256:" + BASE_CONFIG,
               "base_catalog_sha256": BASE_CATALOG, "base_l0_sha256": BASE_L0, "image_ref": ref,
               "manifest_digest": "sha256:" + mhex, "config_digest": "sha256:" + chex,
               "layer_digest": "sha256:" + lhex, "layer_bytes": len(layer), "layers": 86,
               "images_sha256": catalog, "l0_sha256": sha(l0), "l0_bytes": len(l0),
               "boot_volume_sha256": boot["sha256"], "boot_volume_bytes": boot["bytes"],
               "source_overlay": overlay, "prelaunch_field_accessed": False,
               "oci_delta_requires_base_layers": True, "missing_base_layer_descriptors": old_m["layers"],
               "toolchain": {"python": platform.python_version(), "zlib": zlib.ZLIB_RUNTIME_VERSION,
                             "packager_sha256": sha(Path(__file__).read_bytes()),
                             "init_template_sha256": sha(template), "boot_tool_sha256": sha(a.boot_tool.read_bytes())},
               "qualification": {"source_published": False, "final_runtime_executed": False,
                                 "gpu_qualified": False, "published": False, "deployed": False}}
    write(a.out / "candidate.json", pretty(receipt))
    write(a.out / "release.delta.json", pretty({"base_commit": COMMIT, "base_tag": old_release["tag"],
          "base_catalog_sha256": BASE_CATALOG, "inputs": old_release["inputs"], "source_overlay": overlay,
          "images": {**old_release["images"], "k3": {"ref": ref, "config_digest": "sha256:" + chex, "layers": 86}},
          "images_sha256": catalog, "l1": old_release["l1"], "l0": {"bytes": len(l0), "base64_bytes": len(base64.b64encode(l0))},
          "new_layers": 1, "reused_layers": len(known), "boot_volume": boot,
          "artifact_kind": "candidate delta, not a complete stock release bundle", "prelaunch_field_accessed": False}))
    result = check(a.out, a)
    write(a.out / "metadata-check.json", pretty(result))
    hashes = {str(p.relative_to(a.out)).replace("\\", "/"): sha(p.read_bytes())
              for p in sorted(a.out.rglob("*")) if p.is_file()}
    write(a.out / "artifact-sha256.json", pretty(hashes))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--stack", choices=("mixed1", "runtime2"), default="mixed1")
    parser.add_argument("--patched-source", type=Path)
    parser.add_argument("--original-source", type=Path, default=VERSION / "tests/fixtures/processors/kimi_k3.py")
    parser.add_argument("--patch", type=Path, default=VERSION / "patches/models/kimi/0001-mixed-image-unwrap.patch")
    parser.add_argument("--init-template", type=Path, required=True)
    parser.add_argument("--boot-tool", type=Path, required=True)
    args = parser.parse_args()
    require(args.command != "build" or args.stack == "runtime2" or args.patched_source is not None, "patched_source_required")
    result = build(args) if args.command == "build" else check(args.out, args)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except GateError as error:
        print(json.dumps({"passed": False, "gate": str(error)}))
        raise SystemExit(1)
    except Exception as error:
        print(json.dumps({"passed": False, "error_type": type(error).__name__, "details": "suppressed"}))
        raise SystemExit(1)
