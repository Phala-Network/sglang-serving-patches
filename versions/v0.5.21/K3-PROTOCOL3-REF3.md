# Kimi K3 protocol3-ref3: bounded Schema support repair

Valid tool schemas containing a single-field presence condition, or a transparent one-branch `allOf` reference target with string-length siblings, could be rejected before generation by protocol3-ref2. This maintenance release adds exact, bounded support for these shapes while retaining strict constrained generation.

- Lower object `if: {required: [a]}` / `then: {required: [...]}` without `else` to the existing dependency representation. The new path proves property-value support, preserves original assertions and existing oneOf disjointness checks, and retains resource limits.
- Normalize single-branch `allOf` reference targets after resource binding. Preserve dialect scope and depth/node budgets; keep complex non-string leaves and unproven intersections rejected.
- Leave dependencies, tokenizer, CUDA kernels, scheduler and ordinary non-conditional behavior unchanged. This is not general JSON Schema completeness and does not remove strict-mode refusals for unsupported shapes.

Source: `23345268e1da773c46a451a1c0d5bb17e9c5965d`, based on the exact ref2 maintenance source `edcee8c698318ef12910aca3b2571097637d79cd`. All 29 ordered patches were replayed from official v0.5.21 to the expected complete source tree. The image derives from ref2 digest `sha256:59cf8ba0a8d3aa45dd9592f3aa9de8264da9484d9bc524313ba7308c2be0fa04` and replaces only the two reviewed Python implementation files.

CPU evidence uses synthetic schemas, the original-schema validator, native XGrammar matching, dialect/reference regressions and bounded compile-cost samples. These results do not establish recovery of the unavailable production request payloads, GPU throughput or per-user success rates. The final installed-image checks and CLI packaging gate are recorded separately before publication. No production inference probes were sent; current authorization keeps those paused. Deployment is scoped to node 101; nodes 102–104 do not consume this candidate automatically.

The candidate retains explicit refusals for complex conditions, unproven oneOf overlap, multi-branch allOf and unsupported reference intersections. A lower HTTP400 count alone is not semantic correctness; output/stream errors and cancellations must be evaluated separately during production observation.

Final installed-image validation: 394 tests and 32 subtests passed, including the combined conditional/reference regression; direct `hf --help`, `hf download --help` and `sglang --help` passed. Tests used no product overlays, no GPU and no network. Test containers were removed after verified exit.
