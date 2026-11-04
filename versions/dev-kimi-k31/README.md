# Official Kimi K3.1 compatibility maintenance

This ordered source export uses the exact official developer image source
`afcd7d6b487a9cbe73e25941971b4cc107e6f9ae`. It is not a SGLang 0.5.21/0.5.22
upgrade and does not change their maintained patch stacks.

Complete engine: [`254af1d9de5eb6baf68d72e961dcb3116969acfa`](https://github.com/Phala-Network/sglang/commit/254af1d9de5eb6baf68d72e961dcb3116969acfa).
Source release: [`phala-dev-kimi-k31-2`](https://github.com/Phala-Network/sglang/releases/tag/phala-dev-kimi-k31-2),
on the approved `codex/kimi-k31-pro-20261105` compatibility line.
Image2 publication and final-image qualification are pending; the source Release
will record its immutable image digest and qualification receipt.

[series](series), [manifest](manifest.json) and [actual replay](replay.json)
bind all four source-derived steps and their exact intermediate trees:

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
