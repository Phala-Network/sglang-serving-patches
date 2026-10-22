# Necessary Xing4 migration ledger

The candidate starts at official SGLang v0.5.22; it does not apply the old 71-patch selection.

| Contract | Source retained or adapted | Boundary |
| --- | --- | --- |
| Xing config/model/tokenizer/parser/native schema | Exact closure module bytes where API-compatible; 57d3ef390, 2c2f6fcf0; .22 layer-boundary/MLP/final_norm API adaptation | BF16 weights, TP1, fused mHC default; no kernel source changes |
| Native BCG | bf51a8359, bf57ab1c1 | Live batch/padding/stale rows and base2-to-natural LSE; FI .7.1 ragged launcher still returns base2 |
| Compact FP8 cast | 20261017 prefill-compact.patch | Retain .22 kv_loc_plan; upstream SATFINITE is distinct |
| Native public budget | 48e9fc7d5 plus production Q2 guard; explicit true-AR eligibility | Full262144 or reject, no clipping. Q2 and prior fixed-Q4 tuples keep8scratch; AR=None has0scratch. page64 only |
| Auth | 4567f975d adapted to .22 resolution | Explicit TOKEN opt-in; runtime IPC real keys, diagnostics redacted; dumps redact resolved state |
| Allowed tools | 45006bc54, 6136280bb, 3efd2ba5c | All declared tools recognized, allowed subset enforced; message.tools included; stream backend closed on terminal/error/cancel |
| Reasoning/usage | dbdb5349c required generic portions; 0ee2ae9a3, e8c0969c1 | Visibility/strict native bounds/actual emitted usage. Qwen-only effort helpers excluded |
| Schema/SO closure | 62f67f966, 9cea17813, 7c8b1edfe; exact native tool schema and fallback | Original matcher proof; at most32 closer/EOS tokens; no missing-value synthesis; cache/future .22 PP sync retained |
| XGrammar | Existing0.2.7 control-only qualified wheel/patch | Same Python3.12 ABI and exact native library hash;41 bounded escape limitations remain |
| Excluded | 9e36fa2ee, 6e675ced2 unused coercions; disabled JSON pre-budget policy; redundant orphan block; request-static512K/YaRN | No unrelated model/runtime/kernel tuning |

Known control limitation: Chat reasoning.max_tokens has no Xing numerical bound bridge; closure only routes this via the Qwen3.5-specific helper. This task preserves that boundary and does not claim new support.
CPU gates do not prove GPU numerical correctness, actual model startup, end-to-end protocol or performance.

Startup compatibility correction: mHC does not consume stage boundaries and retains FFN-owned complete sums; ordinary residual stages use reduce_results=False and allow_fused_down=False. Global check_stage_producers is unchanged. True dense/MoE meta constructors plus the official check and rejected-bad-producer control are covered on CPU. The prior stage-correction immutable image passed25 installed model checks; actual GPU startup subsequently exposed the missing14336 dispatch below.

14336 dispatch correction: official .22 omits14336 from its mHC split-K dispatch while the existing kernels support it. The fourth model-only patch routes hc_mult4/hidden3584/non-DeepGEMM/1..2048 tokens through the existing split_k8, token_block32, hidden_block256 factory and official big fuse. Larger token and other configurations use original .22 dispatch. The standalone initialized fixture passed eager/graph byte equality and2048/2049 shape/dtype/finite checks; the development model captured graphs and served initial nonstream/SSE responses. Existing TileLang static race warnings remain; this is compatibility evidence, with no new absolute numerical qualification or production claim.

## Retained target MoE stream

Step0005 exports the exact previously measured model bytes (`97322c395840df071880f8838b1023874e28c4eaddc37ac1c91820d9e3d51274`). One CUDA stream is owned by each target model and shared by its layers; attention keeps its legacy stream and MoE retains the legacy fallback. The official capture, BCG, fused, row-count and stream dispatch gates are unchanged. The source CPU harness passes3 tests with144 dispatch subcases; CUDA execution is not simulated acceptance.

Step0006 only binds the release IMAGE_VERSION build argument and includes that harness in the installed-image CPU qualifier. No dependency, Governor, kernel, interval, global prefix, varlen, DualGemm or graph8192 change is selected. The production recipe retains graph2048; prior numerical/content failures and final-image/GPU checks remain separate.

The .22 stack is a real compatibility maintenance exception: shared engine main retains its .20 consumers and only links to this complete .22 engine. Main-entrypoint and actual engine/tag commits are distinct identities.
