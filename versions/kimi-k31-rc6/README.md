# Kimi K3.1 rc6 immutable overlays

`runtime2.json` defines the rc6-2 stack: the original mixed-media unwrap,
startup grammar stop-token completeness ([#46645](https://github.com/sgl-project/sglang/pull/46645)),
and final chunked-prefill abort commit handling
([#34153](https://github.com/sgl-project/sglang/pull/34153)). It changes five
runtime files in one small OCI layer over the same fixed 85-layer vendor base.
The grammar adaptation retains the vendor's cache/admission budgets and strict
thinking behavior. The abort adaptation retains mixed-decode, beam ownership and
failed-restore precedence. Dependencies, CCBridge transport, pool geometry and
the existing media identity contract stay pinned.

Build and check the selected runtime2 stack with the same metadata inputs:

```sh
python -B versions/kimi-k31-rc6/build_overlay.py build --stack runtime2 --inputs /path/to/rc6-inputs --init-template /path/to/rc6-init-script.in --boot-tool /path/to/rc6-boot-volume.py --out artifacts/rc6-runtime2
python -B versions/kimi-k31-rc6/build_overlay.py check --stack runtime2 --inputs /path/to/rc6-inputs --init-template /path/to/rc6-init-script.in --boot-tool /path/to/rc6-boot-volume.py --out artifacts/rc6-runtime2
```

The recipe checks exact original fixtures, applies the ordered canonical patches,
checks every final file hash, and packages only those five runtime paths. Added
registered tests remain source-only. It carries unrelated L0 records unchanged,
preserves inherited config semantics and non-K3 catalog rows, and never opens an
application envelope or opaque startup field. The default `--stack mixed1`
retains the original one-file recipe and output identities below.

For installed runtime2 CPU checks, run the original mixed-media command below and:

```sh
python -B versions/kimi-k31-rc6/tests/test_stop_tokens_cpu.py --source-dir /sgl-workspace/sglang/python/sglang/srt/constrained --expect fixed --output /tmp/stop-tokens.json
python -B versions/kimi-k31-rc6/tests/test_prefill_abort_cpu.py --source-root /sgl-workspace/sglang --runtime-root /sgl-workspace/sglang --receipt-dir /tmp
```

These harnesses execute actual installed source AST with CPU boundary doubles.
They establish token-set propagation, strict/budget control behavior and abort
commit/accounting invariants. They do not establish native xgrammar FSM masks,
full runtime import, CUDA/TEE correctness or serving quality. Exact per-file
identities and the unchanged mixed patch identity remain in the stack manifest;
complete private engine Git identity remains unknown.

## Original mixed1 release

This two-line overlay fixes wrapped still images in rc6 mixed image/video input.
The processor previously put `KimiLoadedImage` inside a visual frame tuple;
dimension lookup then raised `AttributeError` before numerical preprocessing.
The [single patch](patches/models/kimi/0001-mixed-image-unwrap.patch) unwraps frames
in a local visual-item copy, preserving original image identity digests and order.

This is a local source candidate with CPU AST evidence. It is a distinct vendor
rc6 baseline and does not select or copy the image4, common or other model stacks.
An immutable overlay image and final-image GPU/service acceptance are pending.

## Fixed baseline and source boundary

[source.json](source.json) pins the inherited OCI image
`sha256:e5ece94b04b0557639a05790aaf607bb0a55848b34fe63e334e4dcbeeafd55f3`,
config `sha256:c25cf0896e0a94ec544500e4b05bb6b62b14ad294a9df17a0fb8124b21e6b57b`
and all 85 ordered layer descriptors. The checked catalog and selected file
hashes bind this baseline; this source task did not rehash all inherited blobs.
The patch SHA256 remains
`68f03eae4ed03b0c0c49de2e2dee56d684f98d063735ac09fca7fd6d5ec848f7`.

The vendor declares private source `kvinwang/sglang@84ed3eae70b610c3ba14866fb2537c7a09c7831c`.
That Git identity is **unverified**: authenticated private access returned 404;
the Phala and public upstream exact-commit endpoints returned 422. An exact-hash
commit search returned no visible results. The layer header inventory did not
find `.git/HEAD` or Git objects; two other Git-path headers remain unclassified.
These facts do not prove the commit is unavailable everywhere.

**Complete engine Git identity: unknown.** This candidate is an overlay over the
fixed vendor OCI base. Its added patch and tests are complete source tracked by
this repository's Git commit. A future source tag/Release and image metadata must
bind that real overlay commit and base image; an older Phala image4 commit cannot
stand in for the private base. No full private source archive is copied here.

## Reproduce and check installed source

Python 3.10 or newer and its standard library are sufficient. Three exact
processor fixtures total 82,331 bytes; their archive paths, layer and SHA256
identities are in the source record. Replay reads the canonical patch and applies
it only in memory:

```sh
python -B versions/kimi-k31-rc6/tests/test_mixed_media_ast.py --source-dir versions/kimi-k31-rc6/tests/fixtures/processors --expect replay
```

Run the same regression against the actual final installed files, with no overlay
mount or source mutation:

```sh
python -B versions/kimi-k31-rc6/tests/test_mixed_media_ast.py --source-dir /sgl-workspace/sglang/python/sglang/srt/multimodal/processors --expect fixed
```

`--expect baseline` verifies the original failure; optional `--output receipt.json`
writes a portable receipt. All modes verify exact source hashes first. The
[local replay receipt](tests/validation.json) reproduces three wrapped mixed-media
failures on the baseline and passes nine candidate cases through the first
numerical preprocessing boundary, checking PIL/Tensor types, frame order,
timestamps, prompt framing and original identity digests. Real AST functions run
with small dependency/dispatch stubs; GPU decoding, numerical preprocessing and
inference are separate final-image gates. Missing nonstandard `video_tokens` is
an independent accounting observation and is unchanged by this repair.

## Reproduce the metadata delta

[build_overlay.py](build_overlay.py) packages one source file over all 85 inherited
layers without a daemon, registry or VM call. It checks fixed input hashes,
preserves base config semantics and non-K3 catalog entries, and builds an
OCI/catalog/boot delta. The inherited layer payloads remain required. It does not
open application Compose, prelaunch or opaque startup fields.

Pass the fixed vendor metadata directory, stock init template and stock boot tool
explicitly. The original source and patch default to this version's fixture and
canonical patch, relative to the recipe file:

```sh
python -B versions/kimi-k31-rc6/build_overlay.py build --inputs /path/to/rc6-inputs --init-template /path/to/rc6-init-script.in --boot-tool /path/to/rc6-boot-volume.py --patched-source /path/to/patched/kimi_k3.py --out artifacts/rc6-overlay
python -B versions/kimi-k31-rc6/build_overlay.py check --inputs /path/to/rc6-inputs --init-template /path/to/rc6-init-script.in --boot-tool /path/to/rc6-boot-volume.py --out artifacts/rc6-overlay
```

The local build/check reproduced the reviewed candidate's bytes with Python 3.13.3
and zlib 1.3.1. Use that recorded toolchain for the exact gzip/boot transport bytes.
The [source record](source.json) contains the fixed input/tool hashes and full output
identities:

| Output | SHA256 |
| --- | --- |
| OCI manifest | `99a54840a9c1caaf74bb80a4ae944aab6b52c6ae4f99f5775c3aefb558ffc96a` |
| Catalog | `d3886fd3be40519190af8cae4ae698c79b46aafbd23abff9247725b53fdf7c36` |
| Boot volume | `0195fd8cce4a302c4b14122f25a52bf67169c43db33d0a45a8e4bd0a5d1ea75b` |

Patch source commit is `54eba4d1fad647f230ff19d54c30dfbe79377328`.
The maintained recipe belongs to its later containing Git commit; its file hash
is recorded separately. These are distinct source identities. The candidate
manifest preserves inherited config metadata and does not claim a fabricated
complete-engine revision.

The minimal publication path is this Git-verifiable overlay source and recipe
over the pinned OCI base. Recovering the original private Git
objects would improve the inherited source record, but is not a claim made by
this overlay candidate. Publication, tag/Release creation and deployment are
outside this local preparation step.
