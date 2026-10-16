# Frozen SGLang 0.5.21 maintenance

The selected maintenance composition adds retained-token reasoning usage accounting
and DSPARK AUTO folded sampling to frozen control. The common prefetch repair
contains KV/sidecar I/O failures while preserving TP ACK ordering and rejects
stale operation results before allocation or reclamation. Usage is a correctness fix,
not a throughput gain; DSPARK keeps OFF/FORCE and the memory budget fallback.
Dequant memo, direct-read and query-row are excluded from this selected series.

Apply [series](series) on the official base in [manifest.json]: shared frozen-control
patch, shared usage patch, DeepSeek DSPARK patch, then shared prefetch lifecycle repair, common watchdog/failure-state lifecycle,
DSPARK accept-result ownership, and the minimal maintenance image recipe. Existing logical patches
are reused; no second implementation is introduced. Preserve the original control
`phala/` packaging archive after replay to reproduce the complete `engine_tree`.
Both runtime and complete tree were verified with a temporary Git index.

This is the accepted compatibility exception for the existing 0.5.21 maintenance
line; unrelated engine main and other version stacks are not inputs. The patch
repository main maintains these exports alongside its other version directories.
Historical independent variant manifests remain evidence, not selected overlays.

Source and image release: [v0.5.21-phala-watchdog-dspark-fix-20261016](https://github.com/Phala-Network/sglang/releases/tag/v0.5.21-phala-watchdog-dspark-fix-20261016).
The release record binds source, image digest and focused installed-runtime checks.
Final combined model/fleet acceptance is separate. No embedded Governor change;
the external PIG remains an independently versioned component.

The 2026-10-16 repair preserves SGLang SIGQUIT ownership with four Uvicorn workers,
publishes one per-launch terminal latch before fatal cleanup, and makes every
HTTP `/ready` and `/health` fail closed. Hard watchdogs skip blocking diagnostics;
soft diagnostics and serving parameters remain unchanged. Six DSPARK accept-buffer
clones follow open upstream PR #42812 (head `7a8f74963c9db8e21c98ac72cb65ba7b189e6f9c`).
CPU/PyTorch alias negative controls and real four-worker Linux signal regressions
passed; optional CUDA and real target inference remain distinct. No automatic
restart or unique historical GPU root-cause claim is made.
