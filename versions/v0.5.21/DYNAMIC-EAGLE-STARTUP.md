# Xing request-static startup dummy repair

RC5.4 dynamic normal-loader startup stopped before any POST at the strict Q-scale
missing-model-position guard. BaseRunner's autotune dummy directly constructed
ForwardBatch, bypassing request-static initialization. The dummy now supplies its
existing physical-position view as model positions only for an active MLA
request-static layout: the fixed short profile has offset0. Default None remains.
Physical KV, admission/profile selection, Q-scale guards, kernels and graphs are unchanged.

CPU regression calls real Eager buffer allocation, Base autotune dispatch,
run_flashinfer_autotune_forward and _dummy_run with real EAGLE verify metadata and
Q-scale guard. Only process/hardware context and the heavy model forward are stubbed.
RC5.4: dynamic target fails with the original guard error, default target passes.
Repair: both pass, no skips; short BF16 Q is bitwise unchanged including signed zero,
and physical positions/cache locations are unchanged. Actual EAGLE draft startup
uses dedicated graph runners already carrying model positions; the prior17-case
suite's draft capture/restore coverage is reused, not relabeled as draft autotune.

Step0062 preserves all61 prior patch bytes. See
[DYNAMIC-EAGLE-STARTUP-SOURCE-VERIFICATION.json](DYNAMIC-EAGLE-STARTUP-SOURCE-VERIFICATION.json)
for exact source/patch identities and replay. The prior184 affected passes/10 CUDA
skips are retained evidence. Source success is separate from installed image and
real dynamic startup,512K,cache,quality,recovery acceptance. RC5.4 static128 w12
reference is reusable because the existing default-None path is unchanged.
Native long-answer quality failures remain disclosed. GPU6 is not authorized for updates.
