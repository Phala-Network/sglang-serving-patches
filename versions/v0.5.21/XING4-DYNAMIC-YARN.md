# Xing4 request-static 64/128 compatibility candidate

The [complete engine](https://github.com/Phala-Network/sglang/tree/7c19b8bbd723bcb26ba691a19b3e1a7e0cf07f93)
continues the official v0.5.21 maintenance line with the existing compatibility
exception. The canonical [stack](stack.json) and [series](series) preserve the
published 51-step prefix and add source-derived steps 0052/0053, shared startup
diagnostics 0054/0055, stable construction 0056 and forward/terminal API 0057.
[XING4-PATCH-CONTENT.json](XING4-PATCH-CONTENT.json) defines the ordered content
SHA256. The complete tree is `c6ec47142df3a4131455b504bd559fadff3f53f1`.

The implementation preserves native factor64/original4096 and uses factor128
for budgets262145 through524288. Selection precedes clipping and cache lookup;
profiles remain immutable, full math identity isolates caches, and one model
RoPE-position buffer leaves physical positions/KV addresses unchanged. The
backend retains the native attention scalar; long Q is scaled before
quantization. Independent input-page padding/spare-page/sentinel reserve does
not change public capacity or clip original output. Unsupported runtime paths
fail before weight allocation.

Builder201 actually replayed all 57 steps from official upstream
`e00930c5489053f26d86b179cee0d087f846acbb` and matched the complete tree.
Ten affected source CPU files report 159 passed and 10 skipped CUDA cases;
coverage includes retained Qwen policy/graph-buffer behavior, real Xing
ModelConfig/MHA/MLA/scheduler seams, official tokenizers and protected-env auth.
The dynamic author's budget red control reports9 real behavior failures and
2 passes before the budget correction. CPU stubs permit native imports only;
they do not execute CUDA/TileLang or qualify B300 kernels or serving.

Build/test instructions and the flags-only `sglang serve` entrypoint live in
the [engine-owned Docker directory](https://github.com/Phala-Network/sglang/tree/7c19b8bbd723bcb26ba691a19b3e1a7e0cf07f93/docker/xing4).
The [source prerelease](https://github.com/Phala-Network/sglang/releases/tag/phala-v0.5.21-xing4-yarn-rc3)
records the source-to-image identity and focused actual final-image checks.
All four weight/KV evaluation cells must use the same eventual GPU-accepted immutable image.
RC1's two actual GPU native startups exposed a constructor ImportError before
weight loading. RC2 adapts the current dense helper, SCOPED/LOCAL_TAIL enums
and next_sparse declaration argument together. Four full official BF16/FP8
constructor cases actually fail on RC1 source and pass after this repair.
The constructors execute all40 main layers and real mHC/declarations/context;
GPU storage and distributed binding use the real production signatures.
Both actual RC2 GPU startups then completed weight loading and BF16 KV allocation
but failed in prefill graph capture on the old attention slice keyword. RC3 uses
the stable forward, boundary capture/property/postprocess and terminal norm APIs.
Eight full official40-layer CPU forward cases reproduce the original TypeError
and pass after repair, covering BF16/FP8 config, native/dynamic profiles and
empty/nonempty rows. Real MLA/MLP/MoE forward dispatch, context/residual lifecycle
and RMSNorm execute; GPU computation is mocked at actual-signature boundaries,
including mHC kernels and logits. Kernel/RoPE/graph math bytes are unchanged.
GPU scores, throughput, real512K and production acceptance are separate gates.
Shared v0.5.20 main and unrelated maintained integrations retain their existing
contract. This candidate includes no embedded Governor.
