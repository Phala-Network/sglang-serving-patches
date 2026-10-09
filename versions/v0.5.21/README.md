# SGLang 0.5.21 compatibility maintenance

This ordered stack tracks the official 0.5.21 base, separately from the shared
0.5.20 integration. It does not replace or claim to reproduce the 0.5.20 stack.
The exact base, engine commit/tree, patch parents and SHA256 values are in
[manifest.json](manifest.json); apply [series](series) in order.

Seven source-derived logical patches contain common request cleanup, hybrid
storage correctness/batching, Kimi tokenizer and prefill graph changes, and FP8
prefix commits. Kimi fast-path origins are upstream PR39196, PR39696, PR40785
and PR42265. Source replay produced the exact complete engine tree.

Qualified development scope: B300 CUDA13, TP8/PP1/DCP1 Kimi-K3/DFlash,
C8/extra_buffer, FP8 KV/FP32 Mamba. CPU regressions and pinned real tokenizer
checks pass. B300 FP8 pool/kernel tests pass; native page_first registered
MHA/MLA transfers and 8 FP32 Mamba transfer cases pass. Two optional native
pointer-query tests skip because the official wheel lacks that symbol; CUDA
UVA fallback is retained. No private old native extension is included.

No embedded Governor is selected; the deployment uses the separately pinned
external PIG v0.12.31. Other model/topology and throughput gains are not claimed.
Final-image and production service acceptance are separate gates.

The source is published as a version maintenance release, preserving shared
main, following the existing 0.5.21 compatibility-release precedent. It is an
explicit exception to the normal release-from-main route, not a replacement
of unrelated shared runtime fixes.

The phala-v0.5.21-2 maintenance fix declines an optional unfinished Mamba checkpoint when all replacement slots remain protected after eviction. It preserves live request state and locks instead of crashing the scheduler. The original 40-slot/C8 pressure reproducer fails on phala-1 and passes on phala-2; 58 focused CPU tests complete with six environment/GPU skips. Production ratio-based capacity and GPU qualification are separate deployment gates. Upstream references: issue43204 and open PR37619/36770/40416; no claim that those PRs are merged.

The phala-v0.5.21-3 repair adapts open upstream PR39787 (head `4acf667dc2a3ce412eb4a8bf47e81b780aa2f230`) for complete initial Mamba admission. The scheduler counts missing working and ping-pong slots for all selected requests; temporary pressure leaves requests queued. Allocation reserves the whole missing batch before mutating request rows and releases it if row allocation fails. It preserves the phala-2 optional-checkpoint fallback, configured ratio and native Mooncake HA. Builder201 reproduced the original ping-pong assertion and passed 101 targeted CPU tests plus 39 subtests without skips. No new collective or global reservation manager was added; final-image and TP8 service acceptance remain separate.
