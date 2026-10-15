# K3 feedback compatibility repair

The source version `phala-v0.5.21-3-k3protocol2` binds complete engine
`3b7091b271fe6b0d62d2f730f4ece18228591533`, tree
`d24d3c9cf23dbb45a38d4dc7c8431d299afbb187`. The
[release selection](releases/phala-v0.5.21-3-k3protocol2.json),
[ordered series](series.k3protocol2) and
[source replay receipt](source-verification.k3protocol2.json) retain the prior
15 protocol1 patches once and append three qualified source increments plus
one build/provenance increment. All 19 source exports, intermediate trees and
the exact final tree replay from official v0.5.21
`e00930c5489053f26d86b179cee0d087f846acbb` using the existing stack verifier.

The repair preserves constrained JSON marker literals and reference scope,
validates active reference targets reached through annotations, and prevents
automatic-tool parsing from corrupting explicitly constrained JSON. Stream
error cleanup suppresses pending success metadata. The JSON string parser and
grammar assembly avoid unnecessary work while preserving the state machine and
existing cold-compile cost.

The final qualified source feedback suite passed 335 tests with two retained
synthetic-tokenizer skips. Fixed-CPU mechanism measurements are not an
end-to-end throughput or GPU/model claim. Transport read errors, missing-finish
records and usage anomalies still require complete per-request evidence for
attribution. Unsupported schema constraints remain explicit failures.

The engine-owned [build recipe](https://github.com/Phala-Network/sglang/tree/3b7091b271fe6b0d62d2f730f4ece18228591533/docker/phala/kimi-protocol2)
overlays the seven exact qualified product files on the accepted protocol1
image and installs the existing p3 XGrammar wheel with no dependency resolution
or wheel rebuild. Native source `da0ecfb3a758c23650a9bbcc59b7ec15873f9c91`
is reconstructed by the full delta from official v0.2.6rc2, with LICENSE/NOTICE
retained. The [engine Release](https://github.com/Phala-Network/sglang/releases/tag/phala-v0.5.21-3-k3protocol2)
provides the tested CPython 3.12 Linux wheel, SHA256
`5235045af2d459f260d4e85fb3632631de858d91bbeec17adc2e75f21992956a`.
Mooncake and external PIG identities remain unchanged.

The existing v0.5.21 compatibility-maintenance exception applies because shared
v0.5.20 uses a different native/Governor contract. No ancestry merge, shared
selector replacement or GGUF composition is introduced. Shared v0.5.20 and the
49-step GGUF stack/series/manifest remain byte-identical. Source replay does
not qualify the final image or the scoped 101/102 production rollout; those
have separate receipts and the published image's immutable digest.
