# DeepSeek V4.1 Flash source export candidate

This profile reconstructs the full frozen candidate source tree from official
SGLang v0.5.20. It selects 26 source-derived exports: 4 semantically common
changes and 22 model/runtime changes. No Qwen profile, Governor implementation
or TAIL component is implicitly selected.

- Official commit: `94602c9c2b7cbdb8efd5c52802dac6a1c180089e`.
- Frozen candidate: `9acba212f3376c215a9b48a44dcbace15c0982b7`.
- Classified source: `b6a5ec4af0f7981cab954de9a5f4e9ad16fd6948`.
- Both complete trees: `1fa53db30f547b951bb50119a88f2d4cb25c306f`.
- Selection: [DeepSeek profile](../profiles/v0.5.20/deepseek-v4.1-flash.yaml).
- Provenance: [independent manifest](../patches/sglang/v0.5.20/manifest-deepseek-v4.1-flash.json).
- Actual Git-only verification: [evidence](validation/dsv41-source-export.json).

## Ownership and provenance

The common entries are UE8M0 MXFP8 dispatch, completed write-through HiCache
chunk backup, generic service contracts, and the explicit routed-weight ABI.
Common means semantic reuse is possible; it does not mean apply-all, that these
patches work independently of their declared parents, or that another model,
GPU, cache topology or runtime has passed qualification.

The original mixed protocol source commit was split into common service
contracts and model protocol contracts. The common commit retains the async
conversion extension point and serialized ContextVars executor, reasoning usage
cap, media capability/URI validation and exception classification, and
tool-choice-none behavior. The model commit enables the native DSV4.1 encoder,
reasoning-effort/role behavior and the coupled integer-budget protocol adapter.
Historical `dsv41` filenames remain to preserve the exact final bytes; filenames
are not the classification rule. Relevant common tests accompany the common
source commit, and the model commit restores the complete protocol fixtures.

All exports are generated from the recorded source commit and its real parent.
The manifest records full trees, explicit prior-source dependencies, donor
commits and original upstream PRs. The source review field is `pending` until
the corresponding Phala source PR exists; a PR URL does not establish approval.
Donor trailers describe lineage, not byte equivalence after adaptations.
Author and co-author attribution remain in the immutable source commits; raw
diff exports do not replace source history or applicable upstream licenses.

Source code and tests are maintained in Phala-Network/sglang. Do not edit patch
implementation here. Metadata and profile selection belong in this repository.
The existing Qwen manifest/profile and shared source-verifier implementation are
not modified by this addition.

## Deterministic verification

Use the shared `scripts/verify_source_export.py` from the coordinated verifier
change once available in this repository. It currently lives in that change's
working checkout, and this candidate records its exact file SHA-256. This
addition does not copy a second verifier or claim CI integration is complete.

```sh
python scripts/verify_source_export.py \
  --source-repo /path/to/hydrated/sglang \
  --manifest patches/sglang/v0.5.20/manifest-deepseek-v4.1-flash.json \
  --profile profiles/v0.5.20/deepseek-v4.1-flash.yaml
```

The source repository must contain the official base, classified source,
recorded parents and complete input trees. The verifier disables lazy fetching,
checks each source parent/tree and exported SHA-256, re-exports canonical Git
diff bytes, validates selected dependencies and order, then applies only the
selected profile to an isolated index at the official base. Its computed full
tree must equal the profile's expected tree. Verification does not check PR
approval, execute SGLang, build images or contact serving nodes.

Canonical export settings use raw subprocess bytes, `core.autocrlf=false`,
`core.quotePath=false`, and:

```text
git diff --binary --full-index --no-ext-diff --no-textconv --no-color
  --no-renames --unified=3 --diff-algorithm=myers
  --src-prefix=a/ --dst-prefix=b/ PARENT COMMIT --
```

The exact single-line argument vector is recorded per export. The composed
release lock should hash the profile's raw bytes and fix this repository's
commit/tree plus manifest and ordered patch hashes. Do not maintain a second
independent patch selection in that lock.

## Runtime boundary

The frozen base is
`lmsysorg/sglang:v0.5.20@sha256:06e4f2ed21afde4ff513cda65070124e727ba23ccaeff7712b8c40e1097d611f`.
The recorded ABI dependencies include torch 2.13.0+cu130 and FlashInfer 0.6.18.
The changed multimodal and radix-tree Rust extensions require toolchain 1.92.0
and the frozen Cargo locks; the base's other extensions must remain available.
These identities come from the frozen source's PORTING-V0520.md. This export
task did not requalify installed runtime packages or native extension builds.

Model artifact revision, parser/template, topology, effective launch arguments,
optional component identities, final image, protocol and GPU acceptance belong
in the composed release evidence. Source-tree equality allows corresponding
existing evidence to remain attributable; it does not create missing runtime
or production acceptance. The in-flight frozen candidate remains unchanged.
