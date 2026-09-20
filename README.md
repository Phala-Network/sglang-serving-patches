# SGLang Serving Patches

Version-pinned, deterministic exports of serving fixes developed and reviewed
in [Phala-Network/sglang](https://github.com/Phala-Network/sglang). This repository
owns patch applicability, dependencies, order and model profiles; it is not a
second place to hand-edit the same implementation.

## Use and scope

Select an explicit versioned profile, such as
[Qwen3.8-27B on v0.5.20](profiles/v0.5.20/qwen3.8-27b.yaml).
It lists every selected patch in order with its hash. Patches are separated into
[common](patches/sglang/v0.5.20/common), Qwen
[template](patches/sglang/v0.5.20/models/qwen3_5) and
[parser](patches/sglang/v0.5.20/models/qwen3_coder) directories.
Common describes semantic scope, not automatic inclusion or universal
model/GPU/topology validation.

Each [manifest entry](patches/sglang/v0.5.20/manifest.json) records the real source
commit, parent, dependencies and original-source review PR. Governor's Rust
core, Python adapter, policy API and minimal hooks remain in
[its own repository](https://github.com/Phala-Network/phala-inference-governor).
TAIL owns transport and attestation.

Deployment build configuration in phala-models-compose pins these sources
independently. Composed images publish to **ghcr.io/phala-network/sglang**,
associated with Phala-Network/sglang.

## Current candidate

[Qwen3.8-27B review index](docs/QWEN38_REVIEW_INDEX.md) links 18 source draft PRs,
the explicit profile, full serving/combined-engine compares, deterministic Git
tree checks, CPU regression scope and known gaps. The historical 59 source files
are preserved exactly; the generic correlation regression is now in the source
repair commit. Source approval, final composed-image qualification and the
authorized e4 test deployment remain pending.

The historically qualified initial Governor topology is TP1/PP1/DP1,
non-overlap and no PD, with text/images and radix cache. Do not extrapolate it
to other profiles. Strict dynamic-platform and launch/model measurement gaps
remain disclosed.

See [CONTRIBUTING](CONTRIBUTING.md) for the single source-maintenance workflow
and [migration provenance](docs/MIGRATION.md) for the extraction history.
