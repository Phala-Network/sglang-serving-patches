# Official 0.5.22 maintenance

This is the single ordered source export for official SGLang0.5.22, based on `baa9befa381511cd4d56f83980951e5a45fffc6d`. The complete authoritative engine is [`386bc8376cac5121fe93ccdb75954631a7a4e64c`](https://github.com/Phala-Network/sglang/commit/386bc8376cac5121fe93ccdb75954631a7a4e64c), tree `af69b818250468199e696d43b83b092eb0481c43`; navigation branch `codex/sglang-v0.5.22-maintenance`. Planned immutable tag: `phala-v0.5.22-xing4-altstream-20261022` (publication pending).

[series](series) and [manifest.json](manifest.json) contain six source-derived steps: initial common serving/Xing migration, public budget and declared tools, mHC ownership,14336 host dispatch, model-owned target MoE stream, and image version/qualification packaging. The original four patch bytes are unchanged. Their initial cross-layer migration remains one audited step; common fixes are not copied into a second model profile. [Migration ledger](MIGRATION-LEDGER.md) records ownership, dependencies and limits.

[Actual replay](replay.json) used a new Git index from the pinned upstream base and matched every intermediate tree and the final tree. The new source CPU harness passed3 tests/144 dispatch subcases. Build recipes and installed-image checks live in the engine under `docker/xing4-0522`; final-image, real GPU, model/protocol, content, context and performance acceptance are separate. Existing numerical/content failures and41 XGrammar bounded-escape limitations remain visible. No production qualification is claimed here.

The frozen recipe retains BF16 weights, FP8 KV, TP1, native262144, EAGLE1/1/2, chunk8192, graph2048 and HRRN. Governor is not added or selected. External PIG and shared Mooncake remain independent retained components. No graph8192, varlen, DualGemm, interval, global prefix or kernel-source change is included.

Shared engine main retains official0.5.20 for other active consumers. Its .22 documentation entrypoint is distinct from the complete .22 maintenance source/tag. Runtime image publication will use `ghcr.io/phala-network/sglang`; the immutable image digest and acceptance receipt are pending final build/test.
