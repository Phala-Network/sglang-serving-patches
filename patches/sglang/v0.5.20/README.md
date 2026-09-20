# SGLang v0.5.20 serving patches

Upstream: `sgl-project/sglang@94602c9c2b7cbdb8efd5c52802dac6a1c180089e`.
[manifest.json](manifest.json) freezes the ordered patch hashes. Profiles explicitly select common repairs first,
then selected model packs and record their complete pure-serving `expected_tree`. Common is not an implicit apply-all default. Nothing in this repository requires
installing or enabling Governor.

| Directory | Scope |
| --- | --- |
| `common/` | Control-message correlation, lifecycle/SHM cleanup, worker metadata, grammar identity, ownership/queue diagnostics, TOKEN auth/redaction, protocol/schema validation, generic reasoning bounds/visibility, media validation and watchdog behavior |
| `models/qwen3_5/` | Qwen template system-message folding, effort aliases/budgets and tool reasoning history; Qwen3.8 uses this template family |
| `models/qwen3_coder/` | Qwen XML/parser argument coercion and parallel/required tool-call behavior |

The Qwen3.8-27B deployment explicitly selects **both** model packs in that order.
Neither is a default for other models. Each model pack was also applied and AST
checked separately on common without Governor.

`PIG_AUTH_FROM_TOKEN` is retained as the existing serving-auth compatibility
switch. Its spelling does not make it a Governor dependency. Common contains no
`pig_governor` imports. The Governor minimal hook patch is applied optionally
after this serving series, from its independently pinned repository.

The extraction reviewed all seven historical mixed patches, not just patch 7.
Original patch 1's nonce/cancellation-safe control behavior belongs to common;
only its policy route, scheduling/measurement hooks and extension payload stay
in Governor. Original patches 2–6 belong to common. Patch 7 is split by behavior,
including within shared source hunks.

[Reproduction evidence](../../../docs/validation/split-reproduction-r1.json)
proves six patch combinations apply and parse, and the complete Qwen+Governor
combination exactly reproduces all 59 historical frozen files. It does not prove
new image builds or live deployment. Common no-Governor execution regressions now passed; see the review index.
Historical inputs and provenance remain at Governor commit
`b24dbadb3a8a9a1c701bb8cac12bd7648a0bb157`, including the seven original patch
hashes in its versioned release manifest.

Combined images belong to `ghcr.io/phala-network/sglang`, not either patch
repository. Deployment build configuration pins both source repositories and
selects the model packs.

Service implementation is maintained in Phala-Network/sglang source PRs. This
candidate now has 18 source commits, draft PR links and full Git tree export
verification. Approval and image acceptance remain pending; see ../../../CONTRIBUTING.md.

[Current source/PR review index](../../../docs/QWEN38_REVIEW_INDEX.md).
