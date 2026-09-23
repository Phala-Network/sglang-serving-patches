# Unified Patch Maintenance

`scripts/stack.py` is the default consumer entry point. It automatically combines
the protected base series and the one `active_selector` in `selectors.json`.
There is no model selector argument and no second list of patch bytes to maintain.
The historical selectors and failed replay records remain evidence, not separate
model release workflows.

## Current Candidate

- Official source: `94602c9c2b7cbdb8efd5c52802dac6a1c180089e` (`v0.5.20`).
- Active engine: `db0a9f1ec46a3d417d7be190ebc0ce654dad9abd`.
- Engine tree: `93fba1f82c9298c0d16aa192d0e2e312eb77f36d`.
- Ordered engine stack: 31 protected steps plus 62 successor steps.
- New increments: framework log privacy/health cleanup and configurable DSA
  ordinary-memory reserve, with its original 128 GiB default; shared HugeTLB
  accounting for staggered Kimi allocations without changing the DSA ledger.
- These are source candidates. Native dependencies, every target configuration,
  the final image and production deployment are not qualified by replay.

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

After resolving or removing patches with evidence, commit the combined source,
regenerate the ordered exports and update the active version binding together.
Automating that next-version export refresh is still pending; the current tool
does not pretend to rewrite the protected version's historical records.
With no newer official release selected, same-base rehearsal proves the mechanics,
not a successful cross-version migration.

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

- `cpu`: shared privacy, health, initial SSE status, host-reserve, HugeTLB
  accounting and eight-process DSA allocation/rollback contracts.
- `model-fixtures`: existing model protocol fixtures. Supply their required
  tokenizer/template artifacts; missing fixture skips are not a pass.
- `simulator`: upstream paged decode, cache tiers, HTTP/trace replay and prefix
  reuse with the bundled small configuration.
- `simulator-aic`: the original upstream AIC OFFLINE/BLOCKING test, requiring the
  documented `aiconfigurator==0.10.0` setup. A replay-based experiment does not
  substitute for this test.

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
