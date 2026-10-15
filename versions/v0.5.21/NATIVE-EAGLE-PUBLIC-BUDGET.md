# Native Xing EAGLE public context

A real native request with261888 input IDs and256 requested output tokens was
rejected because four EAGLE draft slots were added to its public input length.
Removing only that frontend addition still permits worker/scheduler output clips.
Step0060 separates that public budget from internal speculative storage.

The scoped recipe is native factor64/original4096/context262144, BF16 unquantized
weights, E4M3 KV, CUDA TP1/PP1/DP1/CP1/DCP1, page64, EAGLE3/topk1/draft4,
nonadaptive/single-layer, TRTMLA for effective prefill/decode/draft backends,
and speculative attention mode prefill. Other configurations retain prior behavior.
The patch preserves default prefill graph. Dynamic request-static YaRN continues
to reject EAGLE; full prompt262144 with zero output retains its old input bound.

Frontend/worker/scheduler preserve raw input and requested output. Public overflow
or insufficient total KV capacity rejects without silently clipping the admitted
budget. Native null output fills the remaining context. RoPE keeps the original
262144 rows bitwise unchanged and appends eight native-frequency rows. FI/TRT
internal index/graph tables add eight slots. Existing reserve8 and request-row
headroom71 cover page-rounded allocation; the real page64 allocator spare-page
check replaces a redundant handwritten extra8 reserve after executed ablation.
Req final speculative acceptance retains its existing emitted-output/usage cap.

The [source receipt](NATIVE-EAGLE-BUDGET-SOURCE-VERIFICATION.json) records exact
source/patch/test hashes, all60 intermediate replay trees, frozen-baseline15-fail/
1-pass control and affected166-pass/10-CUDA-skip results. Dedicated16 CPU cases
execute actual validation, Scheduler/Req intake, allocator sizing, ModelConfig,
RoPE math and backend metadata construction. CUDA-only wrappers and kernel entry
points are isolated for CPU checks; no GPU inference is claimed.

The existing image recipe packages the new test via committed-only export and
verify_cpu.sh. Final installed-byte/CPU and G7 boundary/VERIFY-tail/recovery gates
must be recorded against the eventual immutable standard-production image.
