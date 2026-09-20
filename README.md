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

## Source export verification

Each profile records the complete pure-serving Git `expected_tree`. The
reusable verifier checks the selected source commit parents and trees, rebuilds
each patch with the canonical binary Git diff, validates profile order and
explicit dependencies, and applies the selected patch bytes to a separate Git
index from the pinned upstream commit. It then compares the resulting complete
tree with `expected_tree`.

The regenerated diff fixes `core.quotePath=false`, binary/full-index output,
no external diff or text conversion, no color or renames, three context lines,
the Myers algorithm, and `a/`/`b/` prefixes. The record exposes that exact
argument list and proves equivalence by comparing its bytes to every selected
patch file.

It accepts an already hydrated local source object database and never fetches,
checks out, builds, or executes SGLang source. Transient index and tree objects
are written outside the supplied source object database. A partial/promisor
clone with a missing tree or blob fails closed with the missing object
identifier. Run it with the source fork containing the immutable objects:

```text
python3 scripts/verify_source_export.py \
  --source-repo /path/to/Phala-Network-sglang \
  --manifest patches/sglang/v0.5.20/manifest.json \
  --profile profiles/v0.5.20/qwen3.8-27b.yaml
```

Its JSON record includes the raw manifest/profile SHA-256 values, ordered
source/patch bindings, and `computed_tree`. It sets `provenance_verified` only
after those Git checks pass. `review_approval` remains `not_checked`: a source
PR URL or Git proof is not review approval. An image preparer can consume this
same verifier with `additional_patches=[(label, raw_patch_bytes)]` and an
`expected_composed_tree`. It first proves the pure-serving tree, then applies
those bytes in the same temporary index and reports `computed_composed_tree`
plus their SHA-256 values. Additional component provenance remains
`not_checked` here; Governor evidence and review stay separate.

Deployment build configuration in phala-models-compose pins these sources
independently. Composed images publish to **ghcr.io/phala-network/sglang**,
associated with Phala-Network/sglang.

## Current candidate

[Qwen3.8-27B review index](docs/QWEN38_REVIEW_INDEX.md) links 20 source draft PRs,
the explicit profile, full serving/combined-engine compares, deterministic Git
tree checks, CPU regression scope and known gaps. The initial extraction preserved 59 historical source files exactly. Two subsequent review repairs add schema-reference isolation and allowed-tools output enforcement; they have separate red/green and affected-regression evidence. Source approval, final composed-image qualification and the
authorized e4 test deployment remain pending.

The historically qualified initial Governor topology is TP1/PP1/DP1,
non-overlap and no PD, with text/images and radix cache. Do not extrapolate it
to other profiles. Strict dynamic-platform and launch/model measurement gaps
remain disclosed.

See [CONTRIBUTING](CONTRIBUTING.md) for the single source-maintenance workflow
and [migration provenance](docs/MIGRATION.md) for the extraction history.
