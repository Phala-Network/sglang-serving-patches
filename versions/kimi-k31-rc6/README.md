# Kimi K3.1 rc6 mixed-media overlay candidate

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

The minimal publication path is this Git-verifiable overlay source plus its
packaging recipe over the pinned OCI base. Recovering the original private Git
objects would improve the inherited source record, but is not a claim made by
this overlay candidate. Publication, tag/Release creation and deployment are
outside this local preparation step.
