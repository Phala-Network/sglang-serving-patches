# Xing4 request-static 64/128 compatibility candidate

The [complete engine](https://github.com/Phala-Network/sglang/tree/2b3cf0096c9ccc2562c784042afac3f22a10e22b)
continues the official v0.5.21 maintenance line with the existing compatibility
exception. The canonical [stack](stack.json) and [series](series) preserve the
published51-step prefix and add one source-derived logical step0052.
[XING4-PATCH-CONTENT.json](XING4-PATCH-CONTENT.json) defines the ordered content
SHA256. The complete tree is `478b624f8a0c4455634692716a80c126fad914c6`.

The implementation preserves native factor64/original4096 and uses factor128
for budgets262145 through524288. Selection precedes clipping and cache lookup;
profiles remain immutable, full math identity isolates caches, and one model
RoPE-position buffer leaves physical positions/KV addresses unchanged. The
backend retains the native attention scalar; long Q is scaled before
quantization. Independent input-page padding/spare-page/sentinel reserve does
not change public capacity or clip original output. Unsupported runtime paths
fail before weight allocation.

Builder201 actually replayed all52 steps from official upstream
`e00930c5489053f26d86b179cee0d087f846acbb` and matched the complete tree.
Nine affected source CPU files report142 passed and10 skipped CUDA cases;
coverage includes retained Qwen policy/graph-buffer behavior, real Xing
ModelConfig/MHA/MLA/scheduler seams, official tokenizers and protected-env auth.
The dynamic author's budget red control reports9 real behavior failures and
2 passes before the budget correction. CPU stubs permit native imports only;
they do not execute CUDA/TileLang or qualify B300 kernels or serving.

Build/test instructions and the flags-only `sglang serve` entrypoint live in
the [engine-owned Docker directory](https://github.com/Phala-Network/sglang/tree/2b3cf0096c9ccc2562c784042afac3f22a10e22b/docker/xing4).
The [source prerelease](https://github.com/Phala-Network/sglang/releases/tag/phala-v0.5.21-xing4-yarn-rc1)
records the source-to-image identity and focused actual final-image checks.
All four weight/KV evaluation cells must use its same immutable image.
GPU scores, throughput, real512K and production acceptance are separate gates.
Shared v0.5.20 main and unrelated maintained integrations retain their existing
contract. This candidate includes no embedded Governor.
