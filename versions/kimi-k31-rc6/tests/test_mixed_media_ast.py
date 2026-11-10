"""CPU regression for supplied rc6 baseline or final installed source files.

No SGLang/Torch/PIL import, model request, package install, or GPU operation.
Real AST bodies execute through loader, mixed construction, image unwrapping,
GPU-wrapper normalization, dimension calculation, prompt expansion and frame
flattening. Small type/tokenizer/array stubs replace third-party dependencies.
The first numerical preprocessing operation is an intentional stop boundary.
"""

from __future__ import annotations

import ast
import argparse
import asyncio
import dataclasses
import hashlib
import json
import math
import sys
import traceback
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional, Union

VERSION = Path(__file__).resolve().parents[1]
PROVENANCE = json.loads((VERSION / "source.json").read_text(encoding="utf-8"))
EXPECTED = {item["name"]: item["sha256"] for item in PROVENANCE["source_files"]}
TARGET = PROVENANCE["patch"]["runtime_file"]
SOURCE: Path


def source_label(name):
    return "python/sglang/srt/multimodal/processors/" + name


def apply_unified_patch(original, patch):
    """Apply the canonical patch in memory, checking every context byte."""
    import re

    lines, patch_lines = original.splitlines(keepends=True), patch.splitlines(keepends=True)
    assert patch_lines[0] == "--- a/" + TARGET + "\n"
    assert patch_lines[1] == "+++ b/" + TARGET + "\n"
    result, cursor, index = [], 0, 2
    while index < len(patch_lines):
        match = re.fullmatch(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[^\n]*\n", patch_lines[index])
        assert match, f"Unsupported hunk header: {patch_lines[index]!r}"
        old_start, old_count, new_start, new_count = match.groups()
        start = int(old_start) - 1
        assert cursor <= start and len(result) + start - cursor == int(new_start) - 1
        result.extend(lines[cursor:start])
        cursor, old_seen, new_seen = start, 0, 0
        index += 1
        while index < len(patch_lines) and not patch_lines[index].startswith("@@ "):
            line = patch_lines[index]
            assert line and line[0] in " +-", f"Unsupported patch line: {line!r}"
            if line[0] in " -":
                assert cursor < len(lines) and lines[cursor] == line[1:], (
                    f"Patch context differs at source line {cursor + 1}"
                )
                cursor += 1
                old_seen += 1
            if line[0] in " +":
                result.append(line[1:])
                new_seen += 1
            index += 1
        assert old_seen == int(old_count or "1")
        assert new_seen == int(new_count or "1")
    result.extend(lines[cursor:])
    return "".join(result)


class Array(list):
    def __eq__(self, other):
        return Array(value == other for value in self)

    def tolist(self):
        return list(self)

    def round(self):
        return Array(round(value) for value in self)

    def astype(self, target):
        return Array(target(value) for value in self)


class Tensor:
    def __init__(self, label="tokens", shape=(0,), values=()):
        self.label, self.shape, self.values = label, shape, list(values)
        self.ndim = len(shape)

    def contiguous(self):
        return self

    def unsqueeze(self, axis):
        return self

    def flatten(self):
        return self

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return Array(self.values)

    def tolist(self):
        return self.values


class PILImage:
    def __init__(self, label, size):
        self.label, self.size = label, size


@dataclasses.dataclass(frozen=True)
class EncodedImage:
    decoded: Any
    content_digest: str


class Video:
    avg_fps = 2

    def __init__(self, label):
        self.frames = [PILImage(f"{label}-{i}", (64, 48)) for i in range(3)]
        self.closed = False

    def __len__(self):
        return len(self.frames)

    def __getitem__(self, index):
        return self.frames[index]

    def close(self):
        self.closed = True


class PreprocessingBoundary(Exception):
    def __init__(self, frames):
        self.frames = list(frames)


def snapshot_media(value):
    if isinstance(value, EncodedImage):
        return types.SimpleNamespace(data=value, content_digest=value.content_digest)
    label = getattr(value, "label", "unexpected")
    digest = "sha256:" + hashlib.sha256(f"decoded:{label}".encode()).hexdigest()
    return types.SimpleNamespace(data=value, content_digest=digest)


def stop_before_numeric_preprocessing(frames, *args, **kwargs):
    assert all(isinstance(frame, (PILImage, Tensor)) for frame in frames), (
        "A KimiLoadedImage wrapper reached numerical preprocessing"
    )
    raise PreprocessingBoundary(frames)


class BaseProcessor:
    @classmethod
    def _is_preprocessed_input(cls, value):
        return False

    @classmethod
    def _load_single_item(cls, value, modality, *args, **kwargs):
        return value.decoded if isinstance(value, EncodedImage) else value

    async def fast_load_mm_data(self, prompt, image_data, video_data=(), **kwargs):
        loaded = [self._load_single_item(value, "image") for value in image_data]
        self.loaded_images = loaded
        return types.SimpleNamespace(
            images=loaded, videos=list(video_data), input_text=prompt, input_ids=prompt
        )

    def process_mm_data(self, input_text, images=None, **kwargs):
        return self._processor(text=input_text, images=images, **kwargs)

    async def process_and_combine_mm_data_async(self, base_output, tokens, **kwargs):
        self.original_sources = list(base_output.images)
        return self.process_mm_data(
            base_output.input_text,
            images=base_output.images,
            sglang_original_input_ids=base_output.input_ids,
        )

    def _artifact_key(self, digest, *args, **kwargs):
        return digest


class Tokenizer:
    def __init__(self):
        self.texts = []

    def encode(self, text, **kwargs):
        self.texts.append(text)
        return [ord(char) for char in text]


def extract(module, names, class_methods=None, class_attributes=()):
    result = []
    for node in module.body:
        if getattr(node, "name", None) not in names:
            continue
        if isinstance(node, ast.ClassDef) and class_methods is not None:
            node.body = [
                item
                for item in node.body
                if (isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name in class_methods)
                or (isinstance(item, ast.Assign)
                    and any(isinstance(target, ast.Name)
                            and target.id in class_attributes for target in item.targets))
            ]
        result.append(node)
    assert len(result) == len(names), (names, [getattr(n, "name", None) for n in result])
    return result


def compile_nodes(nodes, filename, namespace):
    module = ast.Module(
        body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)] + nodes,
        type_ignores=[],
    )
    exec(compile(ast.fix_missing_locations(module), filename, "exec"), namespace)


def build_namespace(k3_text, skip_hash=False):
    np = types.SimpleNamespace(
        ndarray=Array,
        int64=int,
        asarray=lambda value, **kwargs: Array(value),
        count_nonzero=lambda value: sum(bool(item) for item in value),
        linspace=lambda start, end, count: Array(
            start + (end - start) * i / max(count - 1, 1) for i in range(count)
        ),
    )
    namespace = {
        "__name__": "rc6_ast_fixture",
        "Any": Any, "Literal": Literal, "Optional": Optional, "Union": Union,
        "dataclass": dataclasses.dataclass, "replace": dataclasses.replace,
        "hashlib": hashlib, "math": math, "np": np,
        "torch": types.SimpleNamespace(
            Tensor=Tensor, long=int, int64=int,
            tensor=lambda values, **kwargs: Tensor(values=values),
            cuda=types.SimpleNamespace(is_available=lambda: True),
        ),
        "Image": types.SimpleNamespace(Image=PILImage),
        "Modality": types.SimpleNamespace(IMAGE="image", VIDEO="video"),
        "envs": types.SimpleNamespace(
            SGLANG_MM_SKIP_COMPUTE_HASH=types.SimpleNamespace(get=lambda: skip_hash)
        ),
        "snapshot_media": snapshot_media, "is_cuda": lambda: True,
        "SGLangBaseProcessor": BaseProcessor,
        "MediaArtifactCacheMixin": type("MediaArtifactCacheMixin", (), {}),
        "KimiGPUProcessorWrapper": type("KimiGPUProcessorWrapper", (), {}),
        "_gpu_preprocess_images": stop_before_numeric_preprocessing,
        "_fill_transparent_bg": lambda *args: None,
    }
    module = types.ModuleType(namespace["__name__"])
    module.__dict__.update(namespace)
    sys.modules[module.__name__] = module
    namespace = module.__dict__
    common = ast.parse((SOURCE / "kimi_common.py").read_text(encoding="utf-8"))
    compile_nodes(extract(common, {"KimiLoadedImage", "unwrap_kimi_images"}),
                  source_label("kimi_common.py"), namespace)
    common = ast.parse((SOURCE / "kimi_common.py").read_text(encoding="utf-8"))
    compile_nodes(extract(common, {"KimiGridMMDataMixin"}, {
        "_load_single_item", "process_mm_data", "_kimi_config_fingerprint",
        "count_image_placeholders",
    }, {"uses_wide_image_identity"}), source_label("kimi_common.py"), namespace)
    k25 = ast.parse((SOURCE / "kimi_k25.py").read_text(encoding="utf-8"))
    compile_nodes(extract(k25, {"_get_image_dimensions", "navit_resize_config"}),
                  source_label("kimi_k25.py"), namespace)
    k3 = ast.parse(k3_text)
    compile_nodes(extract(k3, {
        "_KimiK3VisualItem", "_format_k3_timestamp", "_video_frame_to_chw",
        "_split_k3_video", "_encode_k3_special_tokens",
        "_expand_k3_image_prompt_token_ids", "_expand_k3_visual_prompt_token_ids",
        "_k3_to_cuda_chw", "_gpu_preprocess_k3_visual_items",
    }), source_label("kimi_k3.py"), namespace)
    k3 = ast.parse(k3_text)
    compile_nodes(extract(k3, {"KimiK3GPUProcessorWrapper"}, {
        "_normalize_visual_items", "_prepare_input_ids", "__call__", "_gpu_call",
    }), source_label("kimi_k3.py"), namespace)
    k3 = ast.parse(k3_text)
    compile_nodes(extract(k3, {"KimiK3ImageProcessor"}, {
        "_resolve_visual_modalities", "_should_defer_gpu_preprocessing",
        "_process_mm_data_uncached", "kimi_content_config_digest",
    }, {"uses_wide_image_identity"}), source_label("kimi_k3.py"), namespace)
    return namespace


def make_inputs(modalities, wrapped):
    images, videos, frames, digests = [], [], [], []
    for index, modality in enumerate(modalities):
        if modality == "video":
            video = Video(f"video{index}")
            videos.append(video)
            frames.extend(frame.label for frame in video.frames)
        else:
            decoded = (PILImage(f"image{index}", (80, 56)) if modality == "pil"
                       else Tensor(f"image{index}", (3, 56, 80)))
            digest = "sha256:" + hashlib.sha256(f"encoded:{decoded.label}".encode()).hexdigest()
            images.append(EncodedImage(decoded, digest) if wrapped else decoded)
            frames.append(decoded.label)
            digests.append(digest if wrapped else snapshot_media(decoded).content_digest)
    return images, videos, frames, digests


def run_case(k3_text, name, modalities, wrapped):
    namespace = build_namespace(k3_text, skip_hash=not wrapped)
    images, videos, expected_frames, expected_digests = make_inputs(modalities, wrapped)
    wrapper = namespace["KimiK3GPUProcessorWrapper"]()
    tokenizer = Tokenizer()
    wrapper._hf_processor = types.SimpleNamespace(tokenizer=tokenizer)
    wrapper._image_token_id = 200000
    wrapper._patch_size, wrapper._merge_kernel_size = 14, 2
    wrapper._in_patch_limit, wrapper._patch_limit_on_one_side = 256, 64
    wrapper._fixed_output_tokens, wrapper._transparent_bg_config = None, None
    wrapper._get_gpu_norm_tensors = lambda: (None, None)
    processor = namespace["KimiK3ImageProcessor"]()
    processor._processor = wrapper
    processor.mm_tokens = types.SimpleNamespace(image_token_id=200000)
    processor.media_proc_cfg = {"in_patch_limit": 256, "temporal_merge_kernel_size": 2}
    processor.mm_feature_transport = "cuda_ipc"
    processor.processor_fingerprint = "fixture-config"
    processor.keep_mm_features_on_device = False
    order = ["video" if value == "video" else "image" for value in modalities]
    request = types.SimpleNamespace(video_data=videos, modalities=order)
    receipt = {"name": name, "modalities": order, "encoded_identity_wrappers": wrapped}
    original_gpu_preprocess = namespace["_gpu_preprocess_k3_visual_items"]
    normalized_visuals = []

    def capture_visuals(visuals, *args, **kwargs):
        normalized_visuals.extend(visuals)
        return original_gpu_preprocess(visuals, *args, **kwargs)

    namespace["_gpu_preprocess_k3_visual_items"] = capture_visuals
    try:
        asyncio.run(processor._process_mm_data_uncached(
            images, [200000] * len(modalities), request
        ))
        raise AssertionError("Numerical preprocessing boundary was not reached")
    except PreprocessingBoundary as reached:
        labels = [frame.label for frame in reached.frames]
        assert labels == expected_frames, (labels, expected_frames)
        receipt.update(outcome="reached_numeric_preprocessing_boundary", frames=labels)
    except AttributeError as error:
        assert str(error) == "'KimiLoadedImage' object has no attribute 'size'", str(error)
        receipt.update(
            outcome="reproduced_AttributeError", exception=str(error),
            source_trace=[{"path": item.filename, "line": item.lineno, "function": item.name}
                          for item in traceback.extract_tb(error.__traceback__)
                          if item.filename.startswith("python/sglang/srt/")],
        )
    assert all(video.closed for video in videos)
    original_sources = processor.original_sources
    still_sources = [source for source in original_sources
                     if not isinstance(source, namespace["_KimiK3VisualItem"])
                     or source.media_type == "image"]
    actual_digests = [processor.kimi_content_config_digest(source) for source in still_sources]
    assert actual_digests == expected_digests, (actual_digests, expected_digests)
    receipt["original_identity_sources_preserved"] = True
    if normalized_visuals:
        expected_order = []
        for index, modality in enumerate(order):
            expected_order.extend([index] * (2 if modality == "video" else 1))
        assert [item.source_index for item in normalized_visuals] == expected_order
        assert all(isinstance(frame, (PILImage, Tensor))
                   for item in normalized_visuals for frame in item.frames)
        receipt["visual_source_indices"] = expected_order
        receipt["normalized_frames_are_raw"] = True
        if wrapped:
            for original, normalized in zip(original_sources, normalized_visuals):
                if original.media_type == "image":
                    assert original is not normalized
                    assert isinstance(original.frames[0], namespace["KimiLoadedImage"])
                    assert normalized.frames[0] is original.frames[0].image
    receipt["prompt_prefixes"] = [text for text in tokenizer.texts if "media_begin" in text]
    if receipt["outcome"] == "reached_numeric_preprocessing_boundary":
        expected_prefixes = []
        for modality in order:
            if modality == "image":
                expected_prefixes.append("<|media_begin|>image 80x56<|media_content|>")
            else:
                expected_prefixes.extend(
                    f"00:00:0{second}.000<|media_begin|>video<|media_content|>"
                    for second in (0, 1)
                )
        assert receipt["prompt_prefixes"] == expected_prefixes
        receipt["ordered_prompt_framing_preserved"] = True
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True,
                        help="Directory containing the three actual processor .py files")
    parser.add_argument("--expect", choices=("baseline", "fixed", "replay"), default="fixed",
                        help="replay applies the canonical patch only in memory")
    parser.add_argument("--output", type=Path, help="Optional JSON receipt; source files remain read-only")
    args = parser.parse_args()
    global SOURCE
    SOURCE = args.source_dir.resolve(strict=True)
    assert SOURCE.is_dir(), SOURCE
    sources = {}
    expected_hashes = dict(EXPECTED)
    if args.expect == "fixed":
        expected_hashes["kimi_k3.py"] = PROVENANCE["patch"]["patched_file_sha256"]
    for name, expected in expected_hashes.items():
        digest = hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
        assert digest == expected, (name, digest)
        sources[name] = digest
    original = (SOURCE / "kimi_k3.py").read_text(encoding="utf-8")
    patch_bytes = (VERSION / PROVENANCE["patch"]["path"]).read_bytes()
    assert hashlib.sha256(patch_bytes).hexdigest() == PROVENANCE["patch"]["sha256"]
    variants = [("baseline" if args.expect == "baseline" else "candidate", original)]
    if args.expect == "replay":
        candidate = apply_unified_patch(original, patch_bytes.decode("utf-8"))
        assert hashlib.sha256(candidate.encode()).hexdigest() == PROVENANCE["patch"]["patched_file_sha256"]
        variants = [("baseline", original), ("candidate", candidate)]
    cases = [
        ("single-image-pil", ["pil"], True),
        ("multiple-images-pil-tensor", ["pil", "tensor"], True),
        ("single-video", ["video"], True),
        ("image-video-image", ["pil", "video", "tensor"], True),
        ("video-image", ["video", "tensor"], True),
        ("image-video-video-image", ["tensor", "video", "video", "pil"], True),
        ("raw-pil", ["pil"], False),
        ("raw-tensor", ["tensor"], False),
        ("raw-mixed", ["pil", "video", "tensor"], False),
    ]
    results = {}
    for variant, text in variants:
        results[variant] = [run_case(text, *case) for case in cases]
    failures = {case["name"] for case in results.get("baseline", [])
                if case["outcome"] == "reproduced_AttributeError"}
    if "baseline" in results:
        assert failures == {"image-video-image", "video-image", "image-video-video-image"}
    assert all(case["outcome"] == "reached_numeric_preprocessing_boundary"
               for case in results.get("candidate", []))
    for name, expected in sources.items():
        assert hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() == expected
    receipt = {
        "utc": datetime.now(timezone.utc).isoformat(),
        "passed": True,
        "expected_source_state": args.expect,
        "scope": "CPU_AST_types_order_prompt_framing_and_identity_before_numeric_GPU_preprocessing",
        "not_verified": ["full_runtime_import", "GPU_decode_preprocess_or_inference", "live_500_stacktrace", "new_immutable_image"],
        "python": sys.version,
        "source_sha256": sources,
        "runtime_file": TARGET,
        "patch_sha256": hashlib.sha256(patch_bytes).hexdigest(),
        "patch_replayed_in_memory": args.expect == "replay",
        "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "candidate_source_sha256": PROVENANCE["patch"]["patched_file_sha256"],
        "dependency_stubs": ["Torch tensor/PIL/NumPy types", "tokenizer", "framework loader/dispatch", "GPU availability true as branch-control only"],
        "production_AST": [
            "KimiGridMMDataMixin._load_single_item/process_mm_data/count_image_placeholders",
            "KimiK3ImageProcessor._process_mm_data_uncached/_resolve_visual_modalities/kimi_content_config_digest",
            "_split_k3_video/_video_frame_to_chw/_KimiK3VisualItem.size",
            "KimiK3GPUProcessorWrapper.__call__/_gpu_call/_normalize_visual_items",
            "_get_image_dimensions/navit_resize_config",
            "_expand_k3_image_prompt_token_ids/_expand_k3_visual_prompt_token_ids",
            "_gpu_preprocess_k3_visual_items until first numerical preprocessing call",
        ],
        "baseline_error_cases": sorted(failures),
        "candidate_cases_reaching_boundary": len(results.get("candidate", [])),
        "results": results,
        "source_files_unchanged": True,
    }
    if args.output:
        output = args.output.resolve()
        assert output not in [(SOURCE / name).resolve() for name in sources]
        assert output not in [Path(__file__).resolve(), (VERSION / "source.json").resolve(),
                              (VERSION / PROVENANCE["patch"]["path"]).resolve()]
        output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8", newline="\n")
    print(json.dumps({"passed": True, "baseline_reproduced": len(failures),
                      "candidate_cases_reaching_boundary": receipt["candidate_cases_reaching_boundary"],
                      "original_identity_sources_preserved": True,
                      "patch_sha256": receipt["patch_sha256"]}))


if __name__ == "__main__":
    main()
