# GLM47 parser and grammar increments

The active shared v0.5.20 stack includes four source-derived increments from
[Phala-Network/sglang PR #122](https://github.com/Phala-Network/sglang/pull/122).
The source commit is `460d63a87c44c5dc9a9fd3837e9cb5b6d5b4e108`, tree
`d093000351737a9e49348f1cb8036c37de0e7433`, extending the prior P11 source
`ce7a79563954a2cb2b2850b9869b7a7192d7d78b`.

| Export | Behavior | Upstream attribution |
| --- | --- | --- |
| 0106 | Exercise buffered parallel calls, argument boundaries and chunk invariance; preserve the unified stack's existing complete-block draining implementation | [#41493](https://github.com/sgl-project/sglang/pull/41493) |
| 0107 | Required/named selection cannot emit ordinary answer text before the mandatory tool call | [#42458](https://github.com/sgl-project/sglang/pull/42458) |
| 0108 | Install GLM47 grammar only for effective, active tools; preserve allowed-tools and strict-tool policies | [#41233](https://github.com/sgl-project/sglang/pull/41233) |
| 0109 | Use template-aware reasoning mode when a reasoning parser is configured | [#42761](https://github.com/sgl-project/sglang/pull/42761) |

A checkpoint that always opens `<think>` must be allowed to close it even when
clients send `enable_thinking=false`. Using the raw flag to construct the grammar
forbids `</think>` while the response parser still treats output as reasoning.
The correction aligns both paths; it does not implement non-thinking generation
for an always-thinking checkpoint.

Both deterministic export checks pass. The unified verifier replays all 166
steps from pinned upstream `94602c9c2b7cbdb8efd5c52802dac6a1c180089e` to the exact
complete tree above. All 34 patch-repository tests pass. The protected baseline,
Governor hooks/runtime ownership, and native dependency locks are preserved.
[Verification receipts](validation/glm47-20261006/deterministic-gates.json) and
[full stack identity](validation/glm47-20261006/stack-verification.json) record the checks.

The maintained-source CPU run passed **570 tests and 1,491 subtests**. Three
unchanged tests failed and reproduce on the prior P11 source in the same environment:

- `TestGlm47SchemaTypes::test_completed_arguments_reset_between_tool_calls`.
- `TestGlm47SchemaTypes::test_plain_strings_still_stream_before_value_completes`.
- `TestNemotron3Detector::test_streaming_tool_start_ends_reasoning_and_noops_finish`.

The first two expect incremental argument fragments despite the existing atomic
complete-block contract. These assertions and the Nemotron failure are retained;
this change does not suppress them or rewrite unrelated behavior. All new stream
and grammar regressions, the full `test_function_call_parser.py`, and the full
OpenAI chat-handler suite pass. The shared regression selection includes the new
GLM47 chunk, required-call and chat-template cases.

This run copied the maintained Python source into a disposable CPU-only r4
container, then started pytest in a fresh interpreter. Its dependencies were
XGrammar 0.2.7, llguidance 1.9.1 and torch 2.13.0+cu130. It does not qualify a built
unified image or the stack's pinned XGrammar 0.2.6+phala.union1/llguidance 1.8.0
image inputs. The [CPU summary](validation/glm47-20261006/cpu-summary.json) binds
source identity, dependencies and compressed raw logs/JUnit files by SHA-256.

The corresponding v0.5.21 changes are separately deployed on USW2. Their exact
source is preserved at
[`validation/glm53-flash-r4-20261006`](https://github.com/Phala-Network/sglang/tree/validation/glm53-flash-r4-20261006),
commit `4fde785913edcdc036a3b0986cc37ca6839adce4`. That installed image is
`sha256:f6dfa2cd0b87bd7b69d48471a1dd6140958461dc3d9cde4bfa3aaa9993f47b05`,
with SGLang `0.5.21+phala.glm53.r4`, Transformers 5.16.1, Tokenizers 0.23.2 and
XGrammar 0.2.7. It serves the GLM Flash checkpoint revision
`da920bb0b9f4a06727223a349e55468e38352348` on eight B300 GPUs, with the
`flashinfer_trtllm` MoE runner, TRT-LLM DSA, TP8 and EAGLE speculation.

| Deployed v0.5.21 r4 check | Result |
| --- | --- |
| Installed CPU tests | 557 passed, 1,451 subtests passed |
| GPU parser probes | 14/14 passed, including five streamed two-call requests and one buffered two-call request |
| Repeated ordinary tool/structured-output cases | 40/40 passed |
| Full 47-template OpenRouter-derived suite | 32 passed, 12 failed, 3 unvalidated; five unsupported vision/logprobs templates skipped |
| Twelve templates repeated five times | 45 passed, 15 failed, zero transport errors |
| Container after validation | Running, zero restarts, no OOM |

The no-tools/false-thinking request now returns visible `4`. Its non-strict tool
counterpart now returns `add(a=2,b=2)` in 45 completion tokens instead of exhausting
2,048 tokens in reasoning. Auto, required, named and none tool choices pass.

The twelve remaining full-suite failures are nine reasoning-disable cases,
developer-role omission, no visible answer within a 500-token budget, and the
large-prompt marker assertion. The 500-token ceiling was obeyed. The large prompt
accepted 810,034 input tokens but quoted a marker from the input. The native
template still always opens reasoning and drops developer messages. Passing the
visible-output assertion for `reasoning-effort=none` does not establish that
reasoning was disabled.

These are direct-backend results using the captured test corpus at
`redpill-ai/redpill-model-tests` commit
`3013863a4bcb3cf7c5f4803efbc1857af5a90bd5`, concurrency two. They do not qualify
Redpill/PIG routing, GPQA accuracy, other models, or the complete maintained
v0.5.20 image. The deployed v0.5.21 source and the maintained v0.5.20 source are
separate immutable inputs; the deployment result must not be relabeled as
unified-stack GPU acceptance.
