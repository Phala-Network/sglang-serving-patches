# SGLang Serving Patches

Version-pinned SGLang serving and model compatibility fixes maintained by
Phala Network, independently of
[Phala Inference Governor](https://github.com/Phala-Network/phala-inference-governor).

## Scope

This repository is the destination for downstream fixes that remain necessary
when Governor is disabled. Examples include request lifecycle and resource
cleanup, worker metadata, grammar and schema handling, model-specific tool
calling and reasoning compatibility, and serving diagnostics.

Governor retains its Rust controller, Python adapter, policy API and the minimal
SGLang hooks needed to integrate those components. TAIL retains its transport and
attestation responsibilities. Deployment configuration composes independently
pinned versions of these projects.

## Patch organization

Keep generic serving fixes separate from model-specific compatibility changes.
For each supported SGLang version, record the exact upstream commit, ordered
patches, patch hashes, upstream issue or PR references where available, and
targeted validation evidence. Model-specific patches should identify the model
and behavior they affect instead of becoming an implicit dependency for all
models.

On upstream upgrades, review fixes individually and retire a patch only after
confirming equivalent upstream behavior and running the relevant regression.
Do not move Governor integration code here merely because it touches SGLang.

## Migration status

Repository boundary established; patch migration is pending. No patches or
runtime images are released from this repository yet. Existing Governor and
model build inputs have not been changed by this initial repository creation.
Migration must preserve patch provenance and passing evidence, then update the
build dependency references without modifying an in-progress frozen build.
