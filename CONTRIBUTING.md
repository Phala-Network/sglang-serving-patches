# Contributing

Implement serving fixes in real source files in Phala-Network/sglang, one issue
and meaningful regression per source PR. Do not hand-maintain a second copy of
the same implementation in a .patch file here. Preserve upstream attribution
and original licenses. Do not reset or force-push existing fork branches/tags.

Export patches deterministically from reviewed source commits, recording the
full source commit, parent baseline, explicit dependencies and review PR. Review
here focuses on applicability, model profile, order/dependencies and evidence;
CI must compare exported bytes with source and reproduce the selected final tree.
A hash field alone is not provenance verification.

Each explicit profile records its pure-serving `expected_tree`; optional
Governor composition is a separate later input and has its own resulting-tree
check. The Git verifier reports source-export proof only and does not treat a
review PR URL or draft/open/merged state as approval.

common/ means semantic scope, not automatically selected or universally tested.
A profile explicitly selects every patch. Family packs are shared once when
their applicability is stated; model-specific behavior never becomes a default
for unrelated models. On upgrades record retained/replaced/removed-in and reason,
compare patch revisions and run affected regressions.

Governor core/adapter/policy/minimal hooks are maintained in its own repository.
Any generated combined engine branch is a read-only derived review view. Images
and deployment locks belong to phala-models-compose and publish only under
Phala-Network/sglang. Runtime image digests belong to postbuild results.

The current extracted candidate has exact-byte composition evidence, but source
PR/export provenance and new regression gates are not yet complete. Do not treat
historical mixed-image validation as acceptance of this new chain.

CODEOWNERS must name actual Phala maintainers verified for the repositories;
upstream defaults are not adopted automatically and no maintainers are invented.
