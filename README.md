# SGLang Serving Patches

The actual ordered, source-derived patches for Phala's SGLang changes. The authoritative engine
source is the complete, real SGLang tree in
[Phala-Network/sglang](https://github.com/Phala-Network/sglang).
Develop, review, test and update engine changes there first.

## Scope

This repository stays populated with reproducible exports of the maintained source.
Common serving fixes and model-specific behavior belong in the complete engine
source. Consolidating ownership does not prove every model or topology works.

Governor retains its Rust controller, Python adapter, policy API and the minimal
SGLang hooks needed to integrate those components. TAIL retains its transport and
attestation responsibilities. Deployment configuration composes independently
pinned versions of these projects.

## Current unified source

Use the [unified maintenance entry point](docs/UNIFIED_MAINTENANCE.md),
`python scripts/stack.py`, rather than assembling model profiles.
The active selector binds engine `ef5fd69265407664e7efad0a3fd2b458c49c7c9a`, tree
`ae44fce033b1736adf1212baf154b04dbdcae82c`: 31 protected steps plus 157 successor patches.
It preserves the shared serving/model stack and adds trusted internal health
with Governor 0.2.10/ABI5, DSV4 decode shared offload, and default-off exact PD
batch completion diagnostics. Its server-only HMAC joins the external request,
actual P/D rooms and native selected transport/terminal byte records. The
independent Mooncake native artifact is required for this diagnostic API.
The shared owner increment adds original writer seed, bounded clear control,
owner-drain consumption, strict master-evidence timestamp validation and correct
storage-query diagnostic batch offsets and identities.
The successor also adds bounded host-pool/schema accounting, finite independent
two-operation seed evidence and compatible clear identities. Host state occupancy
uses a uniquely declared SWA owner snapshot with matching geometry; unknown state
remains explicit. The source CPU chain covers actual constructor IDs0/1 and sealed
v2 operation/key IDs0/1. A fixed-path, one-shot reader late arm captures the
actual queued prefetch context and bounded GET/prefetch/C128 joins after model
startup; ENOENT retains the opportunity until D publishes the seed. These checks
do not qualify live storage or capacity.
Governor runtime is pinned in the active selector;
the protected historical Governor patch bytes remain unchanged.

The gateway preserves explicit `include_reasoning: false`, `true` and omission
through a pinned vendored `openai-protocol` 1.0.0. The focused CPU harness verifies
typed request serialization and loopback HTTP forwarding; installed gateway wheel
and standalone binary acceptance remain separate build gates.
The native `/generate` request also preserves true `cold_shared_read_bypass` through
the ordinary router to both P/D workers while omitted and false requests retain
their default behavior. The final installed Python launcher has its own HTTP gate.

Source replay and CPU tests do not qualify native transport, GPU inference,
DRAM/SSD cross-instance restoration or production. Those gates use the final
immutable image and their authorized target owners. Native dependency and
historical coverage boundaries remain in the linked maintenance records.

The [independent Mooncake manifest](native/mooncake/manifest.json) pins its public
v0.3.13 base, complete patch hash and reproduced tree. CI replays that native
patch independently of the 178-step engine stack. Native source `1df0440` adds
independent owner-drain and backend capture windows. Its full CUDA wheel and
installed native API checks are required before publishing the shared owner image.

## Protected historical baseline

[series](series) and [manifest.json](manifest.json) retain these immutable
historical inputs, not the current unified engine identity:

- Upstream SGLang v0.5.20: `94602c9c2b7cbdb8efd5c52802dac6a1c180089e`.
- Complete engine: `4281309187007db579a2195f40adfd4baa538528`.
- Complete tree: `83dcb00885129cc2afefdce2e169ebba697a9a67`.
- 30 serving/source patches: the prior 20 changes plus nine GLM logical changes
  and their recorded formatting correction. Common code appears once under
  `patches/common`; Qwen and GLM parser changes have explicit model directories;
  the external FlashInfer workspace fix is under `patches/dependencies`.
- One final, explicitly Governor-owned hook step under `integrations/governor`,
  copied byte-for-byte from Governor `631a53919c62e10c57e7b960bc4d443f39818276`.
  Its SHA256 is `ebf6d2a2e8ef4c9a2c768803cbaf50eda7fc580ae0c888b9aff85297ef34b1a6`.
  This is not a serving fix and does not bundle the external Governor component.

The first 30 entries reproduce serving tree `0a1c456602e7dbadacc55449bc64625b2797c3bc`;
the explicit final hook produces the complete engine tree above. The manifest
records every original commit, parent, patch hash, replay predecessor and
intermediate tree. Replay ordering is not a claim of semantic dependence between
unrelated repairs. See [VALIDATION.md](VALIDATION.md) for scope and limitations.

The historical [model maintenance coverage audit](docs/COVERAGE.md), with
[110 source records](docs/COVERAGE.json), distinguishes fixes actually present
in this frozen engine from upstream-covered changes, known residuals and pending
semantic migration. A complete checkout does not mean every historical model
fix was included in engine428. Its original conclusions are preserved; use the
successor mapping above for the current unified engine.

Regenerate using the small [export script](scripts/export.py), then verify:

```sh
python scripts/export.py --source /path/to/sglang --governor /path/to/phala-inference-governor
python scripts/export.py --source /path/to/sglang --governor /path/to/phala-inference-governor --check
python scripts/export_selectors.py --source /path/to/sglang
python scripts/export_selectors.py --source /path/to/sglang --check
```

Both commands replay every patch into a fresh Git index from the official base
and compare every resulting tree. `--check` also requires exact generated bytes.
No per-model profiles, independent model CI or duplicate manual implementation
are required. See [CONTRIBUTING.md](CONTRIBUTING.md).

See [SELECTOR_MANIFEST.md](SELECTOR_MANIFEST.md) and
`selector-verification.json` for current and historical selector distinctions.
The old raw DeepSeek selector retains its expected DS0011 replay failure;
this is not a missing consumer in the adapted current DS0001–0026 tree.
Historical Kimi/Muse partial-source checkpoints and v0.5.19 reference-only
selectors retain their original identities and qualification boundaries.
Reference-only results are not replay passes.

The immutable Phala fork is the implementation source of truth. Each ready or
candidate selector records its fork commit/tree, branch for navigation only,
source parent, ordered patch IDs and hashes. The branch is movable convenience
metadata; commit and tree are the binding identity. Patch files in this repo are
deterministic exports for audit and external consumers, not a second maintained
implementation. Rebase workflow: update the fork source, create a new immutable
commit/tree, regenerate the selector exports and provenance, then replay each
selected set from the pinned upstream base. Do not hand-edit patches to diverge
from the fork or treat a moving branch as a release input.

The single `xgrammar==0.2.6+phala.union1` dependency has 655 installed native checks plus
14 adapter checks are distinct from model/GPU acceptance. Use
`external-dependencies.json` and the engine's `docker/phala-xgrammar/build.py`
to reproduce the native source from public upstream and the exported delta;
no public Phala wheel or native candidate ref is assumed.

The [independent frozen PIG candidate](docs/PIG_PRIVATE_CANDIDATE_20260922.md)
uses engine `e02dfa12...`, not this unified engine. Its receipt records exact
source/image identities, installed-image CPU qualification and the separate
GPU805 acceptance boundary without replacing any active selector.

Runtime image releases belong to `ghcr.io/phala-network/sglang` and bind to the
complete engine source commit. This repository does not establish image or
production acceptance.

## Historical proposals

The superseded profile/export proposals are preserved through archive tags;
[ARCHIVE.md](ARCHIVE.md) records original commits and PRs. Their source, tests
and evidence remain available for selective reuse in the engine repository.
Archival does not mean they were merged, tested together or production accepted.

The maintained branch contains the current patch collection. The four legacy per-profile
Actions workflows remain disabled; historical runs, archive tags and evidence
are retained. No old proposal was blindly merged to produce this export.

SGLang and the retained FlashInfer source carry Apache-2.0 licensing; preserve
their copyright notices. See [LICENSE](LICENSE) and the exact source provenance
in the manifest. Governor integration remains owned by its source repository.
