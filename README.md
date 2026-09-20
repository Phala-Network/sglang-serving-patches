# SGLang Serving Patches

Optional generated exports of Phala's SGLang changes. The authoritative engine
source is the complete, real SGLang tree in
[Phala-Network/sglang](https://github.com/Phala-Network/sglang).
Develop, review, test and update engine changes there first.

## Scope

This repository is not a second implementation or a mandatory release stage.
Common serving fixes and model-specific behavior belong in the complete engine
source. Consolidating ownership does not prove every model or topology works.

Governor retains its Rust controller, Python adapter, policy API and the minimal
SGLang hooks needed to integrate those components. TAIL retains its transport and
attestation responsibilities. Deployment configuration composes independently
pinned versions of these projects.

## Optional exports

If a consumer needs patches, generate them from pinned upstream and complete
engine commits. Record those commits, the engine tree, deterministic export
procedure and relevant validation. The source repository owns that procedure
and its checks. Do not add per-model profiles, independent model CI or duplicate
manual maintenance here. An export is a derived artifact, not the source of
truth. See [CONTRIBUTING.md](CONTRIBUTING.md).

Runtime image releases belong to `ghcr.io/phala-network/sglang` and bind to the
complete engine source commit. This repository does not establish image or
production acceptance.

## Historical proposals

The superseded profile/export proposals are preserved through archive tags;
[ARCHIVE.md](ARCHIVE.md) records original commits and PRs. Their source, tests
and evidence remain available for selective reuse in the engine repository.
Archival does not mean they were merged, tested together or production accepted.

Main contains documentation, not an accepted patch stack. The four legacy
profile/export Actions workflows remain disabled; main has no workflow files.
Historical runs and evidence are retained. No replacement standalone CI is
required for this optional export repository.
