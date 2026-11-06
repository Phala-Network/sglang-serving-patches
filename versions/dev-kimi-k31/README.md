# Official Kimi K3.1 compatibility maintenance

This ordered source export uses the exact official developer image source
`afcd7d6b487a9cbe73e25941971b4cc107e6f9ae`. It is not a SGLang 0.5.21/0.5.22
upgrade and does not change their maintained patch stacks.

Current repair source: [`204565cce1d82988c4f7235c6113fe1883c0f467`](https://github.com/Phala-Network/sglang/commit/204565cce1d82988c4f7235c6113fe1883c0f467),
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
bind all eight source-derived steps and their exact intermediate trees. The
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
