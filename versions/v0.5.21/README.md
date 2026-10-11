# SGLang 0.5.21 compatibility maintenance

This ordered stack tracks the official 0.5.21 base, separately from the shared
0.5.20 integration. It does not replace or claim to reproduce the 0.5.20 stack.
The exact base, engine commit/tree, patch parents and SHA256 values are in
[manifest.json](manifest.json); apply [series](series) in order.

Eight source-derived logical patches contain common request cleanup, hybrid
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

The phala-v0.5.21-4 maintenance repair reserves the selected batch's outstanding Mamba
main/ping-pong slots while cache-mode HiCache restores FULL/auxiliary pools.
Insufficient space defers admission; returning capacity allows a normal retry.
The configured concurrency, context, memory ratio and extra-buffer strategy are
unchanged. Source CPU validation is complete; GPU/TP8, final-image and production
acceptance are separate release gates, not claims made by this source manifest.
The exact eight-patch replay reproduces the manifest engine tree. Patch 0008
includes one portable CPU regression (production method bodies; tree/transport
fixtures), with original-failure, whole-batch, rollback, retry and ablation checks:

```bash
python test/registered/unit/mem_cache/test_mamba_load_back_admission_cpu.py
```

Run it from the reconstructed full source checkout with CPU PyTorch installed.
Optionally pass `--baseline-root /path/to/unpatched/python/sglang/srt` for the
paired red/green control. Full-tree GPU transfers, TP consensus, model outputs,
and final-image/service acceptance remain separate gates. Related upstream
PRs 33773, 36415, 30986 and 36770 address adjacent paths; this candidate retains
the published complete-live-admission and prepared-slot rollback behavior.
