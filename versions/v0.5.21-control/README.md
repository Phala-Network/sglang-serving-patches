# Frozen SGLang 0.5.21 maintenance

The selected maintenance composition adds retained-token reasoning usage accounting
and DSPARK AUTO folded sampling to frozen control. The common prefetch repair
contains KV/sidecar I/O failures while preserving TP ACK ordering and rejects
stale operation results before allocation or reclamation. Usage is a correctness fix,
not a throughput gain; DSPARK keeps OFF/FORCE and the memory budget fallback.
Dequant memo, direct-read and query-row are excluded from this selected series.

Apply [series](series) on the official base in [manifest.json]: shared frozen-control
patch, shared usage patch, DeepSeek DSPARK patch, then shared prefetch lifecycle repair. Existing logical patches
are reused; no second implementation is introduced. Preserve the original control
`phala/` packaging archive after replay to reproduce the complete `engine_tree`.
Both runtime and complete tree were verified with a temporary Git index.

This is the accepted compatibility exception for the existing 0.5.21 maintenance
line; unrelated engine main and other version stacks are not inputs. The patch
repository main maintains these exports alongside its other version directories.
Historical independent variant manifests remain evidence, not selected overlays.

Source and image release: [v0.5.21-phala-offload-fix-20261012](https://github.com/Phala-Network/sglang/releases/tag/v0.5.21-phala-offload-fix-20261012).
The release record binds source, image digest and focused installed-runtime checks.
Final combined model/fleet acceptance is separate. No embedded Governor change;
the external PIG remains an independently versioned component.
