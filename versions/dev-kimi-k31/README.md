# Official Kimi K3.1 compatibility maintenance

This ordered source export uses the exact official developer image source
`afcd7d6b487a9cbe73e25941971b4cc107e6f9ae`. It is not a SGLang 0.5.21/0.5.22
upgrade and does not change their maintained patch stacks.

Current candidate source: [`308921ab7f196ce41e866b878aa6c8565a982033`](https://github.com/Phala-Network/sglang/commit/308921ab7f196ce41e866b878aa6c8565a982033),
tree `c001d76ae187bdcb92be1dfd697edbbc1d0ad109`, version
`phala-dev-kimi-k31-4`. The image4 build and final installed-image qualification
are pending; no image4 digest or GPU/production acceptance is claimed here.
The [frozen image4 recipe](https://github.com/Phala-Network/sglang/tree/308921ab7f196ce41e866b878aa6c8565a982033/docker/phala/k31/video-20261107)
layers the reviewed Python delta over the qualified image3 digest below, retaining
its native and Python dependencies, Mooncake client and external PIG boundary.

The eleven-step export preserves the previous eight patch files byte for byte
and appends these source-derived steps:

| Step | Scope and source |
| --- | --- |
| 9, common | Preserve complete hybrid Mamba/SWA L3 hits when host capacity is short; copy Mamba temporal slots in chunks using a 64 MiB budget with at least one slot. Adapts [48421](https://github.com/sgl-project/sglang/pull/48421) and [47984](https://github.com/sgl-project/sglang/pull/47984); existing ReplaySSM/COW behavior remains. |
| 10, Kimi | Add bounded `video_url` processing, temporal framing, ordered image/video input and visual owner batching, adapting [35325](https://github.com/sgl-project/sglang/pull/35325), [46077](https://github.com/sgl-project/sglang/pull/46077) and [46103](https://github.com/sgl-project/sglang/pull/46103). Clamp reported cached tokens to reported prompt tokens across streaming, non-streaming and usage headers, adapting [35863](https://github.com/sgl-project/sglang/pull/35863). |
| 11, build | Package the frozen runtime and focused installed-image CPU/CLI/HF gates over image3, without installing or changing dependencies. |

Video processing consumes the video stream and supports request `fps` and
`max_frames`; it does not transcribe audio. The staging estimate is bounded by
`SGLANG_K3_VIDEO_MAX_DECODE_BYTES` (default 4 GiB), with decoder calls and visual
preprocessing grouped into at most four frames. This budget excludes codec
internals, encoded uploads, embeddings, KV and GPU workspaces. Cancellation is
checked between native decoder calls and frames; it cannot preempt an active
native codec call. K3.1 video semantics, CUDA graphs, cross-rank behavior and
production memory at full concurrency still require the final-image GPU gate.

Real-import CPU development checks on the image3 source overlay passed all four
serving/model files: **337 tests and 283 subtests, zero failures or skips**.
The focused storage/Mamba CPU classes passed **3 tests and 10 subtests**.
An initial full storage-file attempt had 233 failures, all from existing GPU
fixtures reporting `No accelerator`; its 4 passes and 30 skips are retained in
the execution record. These CPU results do not measure CUDA peak memory or
qualify the final image. Exact ordered replay matches every intermediate tree.

Historical image3 repair source: [`204565cce1d82988c4f7235c6113fe1883c0f467`](https://github.com/Phala-Network/sglang/commit/204565cce1d82988c4f7235c6113fe1883c0f467),
version `phala-dev-kimi-k31-3`. The eight-step export preserves all four image2
patches byte for byte, then adds hybrid-SSM admission/COW retry, replay-aware
HRRN cost, focused CPU regressions and the Python-only incremental image recipe.
The changes adapt open upstream PRs [37612](https://github.com/sgl-project/sglang/pull/37612)
and [44867](https://github.com/sgl-project/sglang/pull/44867); upstream approval or
merger is not claimed. Native dependencies, Mooncake and external PIG stay fixed.

The source-method gate passed 14 cases. Real-import CPU development checks passed
12 cases and 10 subtests, with two explicit baseline-only comparisons skipped.
Published repair image:
`ghcr.io/phala-network/sglang:phala-dev-kimi-k31-3@sha256:08acd79a162875bc9bfded2ff42cd526a8b0b4e1c4f96e32c1997b61246f226b`.
Final installed-image qualification passes 162 CPU tests and 21 subtests, plus
all five packaged-HF cases; SGLang serve, direct HF CLI, native CPU APIs and
source identity pass. The [repair Release](https://github.com/Phala-Network/sglang/releases/tag/phala-dev-kimi-k31-3)
records publication, inherited-layer/dependency checks and build-helper caveats.
CPU checks do not establish GPU/production acceptance or a unique cause of the
2026-11-06 incident; full-budget/HOL and long-fill retry costs remain explicit.

Image2 baseline engine: [`254af1d9de5eb6baf68d72e961dcb3116969acfa`](https://github.com/Phala-Network/sglang/commit/254af1d9de5eb6baf68d72e961dcb3116969acfa).
Image2 source release: [`phala-dev-kimi-k31-2`](https://github.com/Phala-Network/sglang/releases/tag/phala-dev-kimi-k31-2),
on the approved `codex/kimi-k31-pro-20261105` compatibility line.
Historical image2 baseline:
`ghcr.io/phala-network/sglang:phala-dev-kimi-k31-2@sha256:edc2bb25b3c7f7d67a902e0b7e3a99f1ef8a1371e8395f950ecbb06cb9f3db62`.
Final-image CPU qualification passes 150 tests and 11 subtests, all five HF
cases with zero skips, the official verifier, native CPU APIs, the FSS loader
gate and SGLang/HF CLI checks. The source Release records the detailed receipt.

[series](series), [manifest](manifest.json) and [actual replay](replay.json)
bind all eleven source-derived steps and their exact intermediate trees. The
first four established the image2 baseline:

1. Require complete object-byte counts for Mooncake restores, including missing
   and incomplete response lists.
2. Package the complete engine over the fixed official K3.1 native base.
3. Package pinned K3 HF tokenizer/processor implementations and select them
   explicitly; checkpoint directories provide metadata and BPE data without
   executing checkpoint Python.
4. Install the hash-pinned native rail-group client and optional
   `fastsafetensors==0.5.0` wheel, with dependency resolution disabled and focused
   installed-image qualification gates.

The first two patch files retain their exact image1 bytes. The immutable
[`phala-dev-kimi-k31-1`](https://github.com/Phala-Network/sglang/releases/tag/phala-dev-kimi-k31-1)
release preserves that earlier source and validation record.

The native client is separately maintained at
[`467533b2e80a101dfabd4789ed5aa8ab251c24a6`](https://github.com/Phala-Network/Mooncake/commit/467533b2e80a101dfabd4789ed5aa8ab251c24a6),
tag [`phala-v0.3.13.post1-k31-client-1`](https://github.com/Phala-Network/Mooncake/releases/tag/phala-v0.3.13.post1-k31-client-1).
Its exact artifact and CPU harness identities are in the engine-owned
[native source lock](https://github.com/Phala-Network/sglang/blob/254af1d9de5eb6baf68d72e961dcb3116969acfa/docker/phala/k31/native-client.json).
The [fixed build and qualification recipe](https://github.com/Phala-Network/sglang/tree/254af1d9de5eb6baf68d72e961dcb3116969acfa/docker/phala/k31)
describes the official modules retained and the opt-in rail/loader configuration.
Governor is not added; external PIG remains separately versioned.

Canonical patch bytes and every replayed tree match the complete source.
Development CPU checks pass five packaged-HF cases and 26 native worker-policy
cases. Image1's 150 tests and 11 subtests remain its historical development
evidence. Final-image, GPU, dual-rail, real shared KV and production acceptance
are separate receipts in the source Release and deployment repository.
