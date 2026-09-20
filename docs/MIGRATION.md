# Extraction from the historical mixed patch series

Source: `Phala-Network/phala-inference-governor@b24dbadb3a8a9a1c701bb8cac12bd7648a0bb157`.
Official upstream: `94602c9c2b7cbdb8efd5c52802dac6a1c180089e`.
The [historical manifest](validation/historical-mixed-release-manifest.json)
retains all seven original patch hashes and 59 expected file hashes.

| Historical patch | Current owner |
| --- | --- |
| 0001 Governor hooks | Common: cancellation-safe control correlation, nonce wire fields and ordinary reply echoes. Governor: policy route, core hooks, namespaced policy dispatch/payload. |
| 0002 serving cleanup | Common: request generator/disconnect and MM/SHM ownership |
| 0003 metadata/grammar | Common: worker/device metadata, EAGLE handoff and identity grammar mask |
| 0004 observation | Common: request ownership counts and initial queue time |
| 0005 parallel sampling | Common: logical parent ownership before native fan-out |
| 0006 TOKEN auth | Common: CLI TOKEN opt-in and diagnostic redaction; legacy environment switch preserved |
| 0007 compatibility residual | Common: protocol/allowed tools/schema, generic thinking bounds/visibility, pre-MM validation/media errors/watchdog. Qwen template and Qwen parser logic split into explicit model packs. |

Shared-file hunks were split, not merely moved. In particular, the scheduler's
ordinary nonce echoes remain common while its Governor dispatch moves separately;
`serving_chat.py` keeps generic allowed-tool filtering while Qwen effort/history
adaptations require the selected template pack. Schema-aware coercion helpers
remain generic, and only Qwen parser consumption belongs to the parser pack.

The initial consolidated extraction was split into 16 common source commits and two model source commits. Each exported delta applies in the explicit profile sequence, without
historical Governor offsets or imports. The two model deltas are independent
options after common; Governor is an independent final delta. The deployment
for Qwen3.8-27B explicitly selects `qwen3_5` then `qwen3_coder`. These identifiers
describe the template/parser behavior used by that checkpoint, not a claim that
all models need either patch.

The [new reproduction report](validation/split-reproduction-r1.json) records
per-file hashes for six combinations. Full Qwen+Governor equals all 59 historical
files; common contains no `pig_governor` import or enable hook. The generation
script is retained beside the report. Historical CPU reports are prefixed
`historical-`: they establish origin and prior behavior, but do not replace
new no-Governor execution regressions.

Image build ownership is outside either patch repository. Deployment
configuration must pin both source commits and publish the composition to
`ghcr.io/phala-network/sglang`, associated with `Phala-Network/sglang`.
No historical tag or image is overwritten by this extraction.


Current source commits and draft PRs are linked in [the review index](QWEN38_REVIEW_INDEX.md). Independent Git index application reproduced the full source tree after all 18 stages. The earlier four-pack reproduction remains boundary evidence; current patches are deterministic exports of actual fork commits. Generic control-correlation tests now live in the first source commit instead of a second hand-maintained test file here.
