# GLM-5.3 protocol source candidate

Complete engine `bf761530e2b47bd212a94229635d570ca2e1a6b2` adds patches 0050 and
0051 to the existing unified v0.5.21 stack. All first 49 patch bytes remain
unchanged. The official base is `e00930c5489053f26d86b179cee0d087f846acbb`.
All 51 source exports, patch applications and intermediate/final trees passed
exact replay on builder201. Historical mail patches 0047–0049 use 9-character
object abbreviations; run the verifier with
`GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.abbrev GIT_CONFIG_VALUE_0=9` to preserve
their bytes. New patches use full-index deterministic diffs.

For `glm_moe_dsa` with the native always-thinking template and `glm45` parser,
`reasoning_effort: none` closes the final generation prefill and controls both
response parsing and GLM47 grammar mode. Explicit none wins over conflicting
thinking/template flags. Raw input IDs receive the same non-mutating suffix
repair. Unclosed assistant thinking continuations return a client error;
plain/closed prefixes and completed history remain supported.

With strict thinking enabled, omitted effort caps reasoning at 1024 tokens;
explicit `reasoning.max_tokens` supplies a cap. The total output budget reserves
one quarter, up to 1024 tokens, for the answer and also accounts for the thinking
terminator. Explicit native low/high/max efforts retain the official template
semantics. Budgeted requests reuse the existing reasoner backend around GLM47's
answer/tool grammar, preserving native tool and response-format precedence.

Builder201 ran CPU checks in the immutable Phala7 dependency image with network
disabled and no GPU/inference. The six affected files passed 485 tests plus 409
subtests. Eleven unrelated tokenizer-download cases were deselected. The stale
`test_abort_prefix_match` assertion was also deselected after the same failure
was reproduced on pristine Phala7; patch 0041 intentionally permits only exact
IDs and decimal-index children. No unrelated abort test or implementation was
changed.

The complete pipeline regression uses FunctionCallParser, request sampling,
TokenizerManager, scheduler Req, GrammarManager and actual XGrammar/Reasoner
backends. It verifies plain/auto/required tools, default and explicit budgets,
forced closing followed by legal tools/EOS, none/native-high controls, and
response-format precedence. The pinned model tokenizer at
`3e53882c2f6e3a82b95aca80383efed767a4aac2` separately passes default1024 plain
and explicit16 required-tool pipelines; only the final closing token is added
to reasoning-off prompts and native low/high/max prompt IDs match exactly.

Independent agent review resolved the three findings concerning raw input IDs,
open-thinking continuation and full-assistant EBNF budget bypass. This is agent
review, not human approval. Design ablation removed speculative effort tiers,
reused one suffix helper and the existing reasoner wrapper, and removed unrelated
formatter churn with complete-AST equivalence to the tested source.

The engine-owned `docker/phala-glm53-protocol/` recipe exports immutable Git
objects, checks the Phala7 preimage, installs one runtime module and matching
tests, and updates wheel RECORD. It pins the Phala7 base digest and explicitly
labels version `phala-v0.5.21-8`. Source replay, installer checks, a built image,
published digest and GPU/production acceptance are distinct stages; this source
record claims no final-image or serving qualification.
