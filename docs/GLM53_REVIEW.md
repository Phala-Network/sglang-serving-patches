# GLM-5.3 v0.5.20 profiles

These are review candidates extracted from the deployed GLM-5.3 B300 CC-OFF
runtime, not a new image release. Source implementation lives only in the
Phala-Network/sglang issue PRs linked in each profile. Patch files are exact
`git diff --binary --full-index <parent> <commit>` outputs.

Select exactly one profile:

- `profiles/v0.5.20/glm-5.3-mooncake.yaml`: TP8/DP1/PP1, buffer_only,
  write_through/timeout, Mooncake RAM+SSD; prefill graph 4K or16K historical
  acceptance. Does not include host-only asynchronous ACK.
- `profiles/v0.5.20/glm-5.3-host-async-ack.yaml`: TP8/DP1/PP1, host cache,
  write_through, guarded asynchronous ACK, graph4K historical acceptance.

The JSON-formatted YAML profiles are the only patch selection source. The
glm53-sources inventory is provenance, not an implicit apply list. Explicit
ordered dependencies include source-stack prerequisites to reproduce complete
trees; category common does not qualify other models or topologies.

| Ownership | Selected fixes |
|---|---|
| GLM/model family | Atomic glm47 tool streaming; DSA host-budget and strict hugepage allocation |
| Common, explicitly selected | Reasoning usage cap; idle local gauge; SSD rank isolation; completed-chunk write-through; physical-KV admission cap; guarded host-only ACK and its spawn-safe test |
| External dependency | FlashInfer0.6.18 TRTLLM workspace destruction cleanup, Apache-2.0; original copyright retained, source file pre/post hashes in manifest |

Host-only keeps the SSD-isolation implementation inert for exact deployed
runtime equivalence; that is not an enabled Mooncake feature. DSA startup
budget opt-in remains off in the qualified configurations. No GPU CC/TEE,
PD, DP>1, alternate quantization or other model qualification is claimed.
`reasoning_effort=none` remains a Redpill responsibility; the usage cap does
not add request-effort mapping. Governor is disabled and TAIL is not moved.

Verification re-exports every patch from the actual source Git objects,
checks exact bytes and parents, applies only selected patches to the official
baseline in an isolated checkout, checks the complete tree and deployed
python/sglang subtree, then runs source-bound CPU regressions. Added tests
change the full source tree relative to historical deployment; runtime source
and external overlay bytes remain equal. Gloo/GPU/runtime acceptance evidence
is reused only from the matching deployed code/dependency/topology; this
migration is not a new GPU benchmark or new production acceptance.

Potential overlap with the open Qwen common stack must be resolved explicitly
when composing families. GLM reasoning-usage changes schedule_batch accounting;
the Qwen reasoning visibility patch changes a different control path. These
profiles do not automatically select the Qwen stack or claim combined testing.

Historical acceptance: host r11 passed installed-code10KV and14ACK tests
(including real two-process Gloo), host long-prefix/backups/public auth;
Mooncake r10 passed10KV regressions and8internal+2public functional cases,
including actual35008-token storage restore. Near-capacity GPU replay remains
unverified. Existing host TLS static findings are not resolved by source
organization. No image build/publish, production update, or auto-merge is part
of this metadata PR.
