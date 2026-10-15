The native Xing EAGLE budget repair keeps input/output within public262144 and supplies independent internal scratch. The [60-step exact replay](NATIVE-EAGLE-BUDGET-SOURCE-VERIFICATION.json) preserves all59 earlier patch bytes. Dedicated16/16 and affected166 CPU cases pass, with10 explicit CUDA skips. Final-image and GPU gates remain separate; see [the repair contract](NATIVE-EAGLE-PUBLIC-BUDGET.md).

The Xing runtime RC5.2 candidate fixes startup observation through the actual EAGLEWorkerV2 draft-worker property. Source14 affected cases pass on201; the prior installed image reproduces the original AttributeError. All58 earlier patch bytes remain unchanged, and the [59-step exact replay](RC52-SOURCE-VERIFICATION.json) reproduces the complete engine tree. Final-image and GPU/service gates remain separate.

# SGLang 0.5.21 compatibility maintenance

Xing request-static MLA YaRN extends the same ordered stack at steps 0052/0053,
shared startup diagnostics 0054/0055, stable construction 0056 and forward/terminal
API repair 0057. All 56 earlier patch files are preserved. The 57-step replay
matches complete engine `7c19b8bbd723bcb26ba691a19b3e1a7e0cf07f93`; source CPU checks
on 201 report 159 passed and 10 explicit CUDA skips. Actual final-image and
GPU/service acceptance remain separate gates. See
[Xing source and image contract](XING4-DYNAMIC-YARN.md).

The phala-v0.5.21-7 source adds three GGUF increments to the unchanged
published phala-6 46-step prefix. The canonical 49-step [stack](stack.json),
[series](series) and [source/image qualification](qualification.json) bind
complete engine `c2ce5382dad45fd85e39f5d4e1d93165225eb34d`.
The original tested build input is `90adf120aa19e683f95d8702c89e31fb1c3d4ab0`;
subsequent metadata repair changes neither patch bytes nor series.
See [GGUF usage and limits](MODEL894-DYNAMIC-YARN.md). The existing compatibility
release exception below remains in effect; shared v0.5.20 main is preserved.

The `phala-v0.5.21-6` source candidate adds request-static 1x/2x/4x YaRN and
safe retirement of rejected requests. It uses the same official dependencies,
native extensions and complete maintenance ancestry as phala-5. The tested
53f implementation is unchanged apart from CRLF-to-LF source normalization;
the engine-owned build recipe verifies installed bytes and wheel RECORD.
The 46-entry [series](series) includes this source and build packaging.
This continues the existing version line because shared v0.5.20 main requires
the incompatible private XGrammar/native/Governor combination. Source replay,
final image and production qualification remain distinct.

This ordered stack tracks the official 0.5.21 base, separately from the shared
0.5.20 integration. It does not replace or claim to reproduce the 0.5.20 stack.
The exact base, engine commit/tree, patch parents and SHA256 values are in
[manifest.json](manifest.json); apply [series](series) in order.

The original eight source-derived logical patches contain common request cleanup, hybrid
storage correctness/batching, Kimi tokenizer and prefill graph changes, and FP8
prefix commits. Kimi fast-path origins are upstream PR39196, PR39696, PR40785
and PR42265. Source replay produced the exact complete engine tree.

Prior eight-patch qualified development scope: B300 CUDA13, TP8/PP1/DCP1 Kimi-K3/DFlash,
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
The prior eight-patch replay reproduced its recorded engine tree. Patch 0008
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


## Shared maintenance candidate (2026-10-12)

This candidate extends the existing v0.5.21 maintenance ancestry at
`e9a40ece22f8539d434ccc138336019ddbf2e06c` with common serving, request isolation,
privacy and Qwen-family API/parser changes. The original eight patches remain
first in the ordered stack; lifecycle and Mamba fixes are not duplicated.
The source identity and ordered intermediate trees are in [stack.json](stack.json).
Run the shared verifier with `--stack-root versions/v0.5.21`.

The v0.5.20 shared main and its active selector remain unchanged. Official
v0.5.21 reorganized/deleted legacy cache classes and changed native interfaces;
the v0.5.20 Governor-r6 and custom native integration cannot be relabeled as
v0.5.21 without a separate compatibility port. Reusing this existing unified
version maintenance line is the explicit release-from-main exception. It is
not a new Qwen-only stack, a fake ancestry merge, or qualification of all
v0.5.20 features on v0.5.21.

No embedded Governor or old custom XGrammar/KV wheel is selected. Official
v0.5.21 dependencies and native build contract apply. External PIG remains a
separate deployment component. [regressions.json](regressions.json) includes
47 affected CPU files plus the CUDA-only FP8 pool suite, including the retained hybrid-storage, Kimi tokenizer,
prefill gate and FP8 pool paths. Current candidate CPU acceptance and 44-patch exact replay passed; see
[qualification.json](qualification.json). The 47 CPU files contain 1,440 passed
JUnit entries (including subtests) and 2 CUDA-only skips. Final full-wheel
native imports and Qwen GPU/service acceptance require their own evidence;
the prior Kimi GPU results above do not qualify this new candidate.

Abort targeting accepts an exact request ID or decimal-index child ID.
Caller IDs that independently reuse that parent/child naming convention remain
ambiguous; this change does not introduce a complete ownership registry.

Patch 0008 is normalized from its original mail-patch wrapper to the same full-index deterministic diff format as the remaining stack; its source commit and resulting tree are unchanged.

Xing4 native support extends the same stack at steps 0050/0051: the frozen
upstream PR39793 port and stable repairs, then the fixed official SentencePiece
tokenizer installed/registered for data-only model mounts. The canonical
51-step source replay matches the complete engine tree. Twenty focused CPU
cases include both official tokenizer vocabularies and explicit environment
authentication; GPU and final-image checks remain separate. The reproducible
ordered patch-content digest is defined in [XING4-PATCH-CONTENT.json](XING4-PATCH-CONTENT.json).

Step0061 is the isolated [fixed-EAGLE dynamic YaRN source candidate](DYNAMIC-EAGLE.md); source/CPU and exact61-step replay only, no dynamic image/GPU acceptance.
