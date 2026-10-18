# Kimi ref5 DFlash mask release

The [complete source release](https://github.com/Phala-Network/sglang/releases/tag/phala-v0.5.21-3-k3protocol3-ref5-dflashmask1)
is `e77dff2b12ef22ac67b2ea2905e066cedb3f69c3`. The unchanged 31-entry ref5 prefix plus one source-derived
DFlash patch replays to tree `a7fe9fbb9e3c78b245e7b4ece1facafb4fdd5578`; every intermediate tree is verified
in [the receipt](source-verification.k3protocol3-ref5-dflashmask1.json).
The shared canonical series and other maintenance consumers are unchanged.

The increment carries the upstream PR43518 stale-mask repair and its five
regressions. It clears extend/decode state before verify; current tree-position
constraints remain the responsibility of the verify callers. Native XGrammar
p6 and the ref5 dependency identities are inherited, with no strict2 override.

Use [the ordered series](series.k3protocol3-ref5-dflashmask1) and
[frozen source/component manifest](releases/phala-v0.5.21-3-k3protocol3-ref5-dflashmask1.json).
The [exact historical recipe](https://github.com/Phala-Network/sglang/tree/f006757d2b4112de30ff1f3d9cb55de58cf1c3a7/docker/phala/kimi-protocol3-ref5-dflashmask1) is archived in the SGLang repository; its
image digest is linked from the public release receipt. Source
replay is separate from the existing installed-image five-case check and
natural production observation. HTTP400/abort events remain; full-load,
semantic correctness and overall error-rate improvement are not claimed.
