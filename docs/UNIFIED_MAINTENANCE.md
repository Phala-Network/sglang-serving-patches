# Unified Patch Maintenance

`scripts/stack.py` is the default consumer entry point. It automatically combines
the protected base series and the one `active_selector` in `selectors.json`.
There is no model selector argument and no second list of patch bytes to maintain.
The historical selectors and failed replay records remain evidence, not separate
model release workflows.

## Current Candidate

- Official source: `94602c9c2b7cbdb8efd5c52802dac6a1c180089e` (`v0.5.20`).
- Active engine: `106ec8462cf20c8d71c2192accc5f5fa28bb77c4`.
- Engine tree: `53f1dda4c2f4fd8918c95df3a1b36f2dcf99e0fb`.
- Ordered engine stack: 31 protected steps plus 93 successor steps.
- R8 added guarded selective write-through async ACK and refreshed live Kimi
  `inputs_embeds` during prefill CUDA graph replay. R9 preserves DeepSeek
  integer reasoning budgets through the typed request and custom encoder.
- R10 adds GLM-5.3-Flash vision/HiCache corrections, common output and health
  privacy guards, and a DSA partial-construction rollback fix. Streaming usage
  remains forced by the existing protocol contract.
- New increments: framework log privacy/health cleanup and configurable DSA
  ordinary-memory reserve, with its original 128 GiB default; shared HugeTLB
  accounting for staggered Kimi allocations without changing the DSA ledger;
  reviewed SRT privacy migration preserving log controls, required evaluations,
  request decoding, scheduler time gates and business CLI output; one
  registered-KV extension with Hopper/Blackwell code targets and device-scoped
  lazy dispatch, without a raw-address fallback for registered host memory;
  empty-transfer and invalid-quota guards before launch arithmetic.
- These are source candidates. Native dependencies, every target configuration,
  the final image and production deployment are not qualified by replay.

The new KV integration requires both its compiled private wheel and the
matching `sgl_kernel.kvcacheio` wrapper from this engine in the final image.
Installing the private wheel alone does not update the separate `sgl_kernel`
package. The image builder must install and verify that wrapper at build time;
no startup patching or source mounts qualify the final installed image.
CPU compilation and SDK-stub-linked registration are not GPU execution evidence.

Real implementation changes belong in the Phala SGLang fork. The patch files
remain deterministic exports of those immutable changes. Governor-owned hook
bytes retain their component identity; they are validated against their resulting
engine tree even when their original diff format differs from `git diff`.
The existing frozen exporter separately verifies the original Governor artifact.

## Verify and Prepare

Run from this patch repository with a source repository containing the locked
Git objects. Moving branches are never used as immutable input identities.

```sh
python scripts/stack.py inspect
python scripts/stack.py verify --source /path/to/sglang
python scripts/stack.py prepare --source /path/to/sglang --output /new/verified-source
```

Verification checks exported patch bytes and source identities, replays the whole
active stack in a temporary Git index, and compares the complete engine tree.
The source checkout, its index and its branches are left unchanged.
Preparation creates a new detached worktree at the verified engine commit and
refuses an existing output path. It does not build, publish or deploy.

Dependency patch hashes are checked, but this command does not compile native
dependencies or read back their origin repositories. Those boundaries are explicit
in the result. Keep the existing external-source recipe/license checks and the
eventual installed-image ABI gates.

## Upgrade Preflight

Fetch and verify the desired official release separately, then pass its ref or
commit to the same entry point:

```sh
python scripts/stack.py upgrade-check --source /path/to/sglang \
  --upstream OFFICIAL_COMMIT --output /new/upgrade-report.json
```

- `applies`: the patch was actually applied in order to a temporary index.
- `already-present-needs-review`: reverse application succeeds, but that is only
  evidence for review. No patch is deleted and no upstream semantic equivalence
  is assumed.
- `conflict`: application and reverse application both fail. Replay stops there;
  later patches are reported as unchecked, not silently treated as independent.

Only a conflict-free, review-free report returns `ready-for-regression`.
It is not a release acceptance. To materialize that trial as one staged source
checkout, use:

```sh
python scripts/stack.py prepare --source /path/to/sglang \
  --upstream OFFICIAL_COMMIT --output /new/upgrade-source
```

The new worktree starts from that upstream and applies the entire retained stack.
Its index tree must equal the preflight result. It remains uncommitted so source
review and tests precede a new engine identity. The prior source is not modified.
If review is needed, no output checkout is created.

This trial checkout is for inspection/tests. Its uncommitted edits are not
implicitly consumed by the exporter.

## Re-export an Upgrade

```sh
python scripts/stack.py upgrade-export --source /path/to/sglang \
  --upstream OFFICIAL_COMMIT --branch codex/unified-next \
  --output /new/next-stack
python scripts/stack.py verify --source /path/to/sglang \
  --stack-root /new/next-stack
python scripts/stack.py prepare --source /path/to/sglang \
  --stack-root /new/next-stack --output /new/next-source
python scripts/stack.py test --source /new/next-source \
  --stack-root /new/next-stack --suite cpu --suite model-fixtures \
  --output /new/next-results
```

The exporter retains the ordered logical patch IDs, applies each patch in a
temporary Git index, creates a linear source commit per retained patch, exports
its real diff, and verifies the complete result before creating the new local
branch. HEAD, the caller's index and working files stay unchanged. Existing
output paths and branch names are rejected; a concurrent branch creation cannot
be overwritten. A failure while copying final artifacts or creating the ref may
leave an output directory for inspection, not an accepted release.

The result is one `stack.json`, its generated patches, the shared dependency
lock/patches, and the shared regression selection. `upgrade-result.json` records
the executed source verification and its limits. The new format is consumable
by the same commands through `--stack-root`, including a subsequent upgrade.
Patch bytes and resulting trees are reproducible; regenerated commit IDs also
depend on the local Git author/committer identity and timestamps.

On conflict or an already-present patch, export stops without silently dropping
it. Copy the `decision_context` object from `upgrade-check` into a decisions
file and add entries only for reviewed exceptions:

```json
{
  "id": "EXISTING_LOGICAL_PATCH_ID",
  "action": "replace",
  "source_commit": "REVIEWED_REPLACEMENT_COMMIT",
  "reason": "Adapt this fix to the new upstream interface.",
  "evidence": "Review record identifying the changed contract and its tests."
}
```

Pass that file with `--decisions /path/to/decisions.json`. A replacement must be
a single-parent source commit whose parent tree equals the accumulated new
upstream plus earlier retained patches. Construct it in an isolated review
checkout at that position; a whole combined candidate or unrelated donor diff
cannot substitute for that prefix. For a reviewed upstream-covered/superseded
patch use `"action": "drop"` with a reason and evidence instead. Reverse
application alone is not proof of semantic equivalence. Decision context binds
the old patch stack and target commit; stale, duplicate and unknown decisions
are rejected. Tool success records the decision but does not prove its rationale.

After qualification, promote the generated bundle into the existing patch
maintenance checkout and commit it with the new source release identity. A
root `stack.json` becomes the single default active list; do not hand-maintain
it alongside a new per-model selector set. Existing frozen manifests, selectors
and old patch bytes remain historical evidence, not another active release line.
The existing CI verifies both frozen evidence and the actual active stack.
Do not delete prior version history or publish an unqualified source candidate.

With no newer official release selected, same-base rehearsal proves these
mechanics, not a successful cross-version migration. Export does not fetch or
certify an official release, change dependency versions, build native code,
publish an image, enable Governor or deploy.

## One Regression Entry Point

```sh
python scripts/stack.py test --source /new/verified-source \
  --suite cpu --suite simulator --output /new/test-results
```

The existing SGLang CPU environment must provide `pytest`, `psutil`, the simulator
dependencies and the dependencies of the selected fixtures. The command does not
install packages or download weights. Prefer the approved, resource-limited CPU
container on `.201`; the runner disables visible CUDA devices and HF network
downloads, but is not a network sandbox itself.

`regressions.json` owns the one set of test selections:

- `cpu`: framework/SRT privacy, transformation and parser canaries, health,
  initial SSE status, host-reserve, HugeTLB accounting and eight-process DSA
  allocation/rollback contracts.
- `model-fixtures`: existing model protocol fixtures. Supply their required
  tokenizer/template artifacts; missing fixture skips are not a pass.
- `simulator`: upstream paged decode, cache tiers, HTTP/trace replay and prefix
  reuse with the bundled small configuration.
- `simulator-aic`: the original upstream AIC OFFLINE/BLOCKING test, requiring the
  documented `aiconfigurator==0.10.0` setup. A replay-based experiment does not
  substitute for this test.

For the existing pinned model fixtures, supply `MUSE_TEMPLATE` (SHA256
`900db3effc316e33295ec3d7dfa2df83ea2735228cba73adba8fecc2e83343f7`)
and `NEMOTRON_TOKENIZER_JSON` (the qualified input SHA256 is
`623c34567aebb18582765289fbe23d901c62704d6518d71866e0e58db892b5b7`).
These are external test inputs, not vendored weights or template distribution
permission. Record the actual artifact identities with each qualification.
Without the inputs, the suite remains incomplete, not passed.

Every case records its exit code, JUnit counts, log hash and source identity when
available. Zero tests, skips, missing/broken JUnit or a nonzero exit cannot become
a passed suite. Timeouts stop the remaining suite and clean only the owned test
process tree. Existing output directories are rejected to preserve prior evidence.
Source tests, simulator predictions, native/GPU qualification and image acceptance
remain distinct. The same suite definitions can be reused across all deployments;
these are test groups, not model-specific build profiles.

An official upgrade does not automatically require retuning every model.
Run the shared CPU/fixture checks, select additional tests for affected contracts,
and use model/hardware smoke checks where required. Shared kernel or scheduling
changes can require GPU/performance evidence; unchanged applicable evidence can
be reused. Publish one versioned image only after the relevant gates pass.
