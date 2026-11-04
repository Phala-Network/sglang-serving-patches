# Official Kimi K3.1 compatibility maintenance

This two-step source export uses the exact official developer image source
`afcd7d6b487a9cbe73e25941971b4cc107e6f9ae`. It is not a SGLang 0.5.21/0.5.22
upgrade and does not change their maintained patch stacks.

Complete engine: [`03cf254955c2606744c8eafc641822a93244c325`](https://github.com/Phala-Network/sglang/commit/03cf254955c2606744c8eafc641822a93244c325).
Release: `phala-dev-kimi-k31-1`. The user approved the scoped maintenance-branch
release; the shared engine main retains its other consumers.

[series](series), [manifest](manifest.json) and [actual replay](replay.json)
bind both intermediate trees. The common repair requires exact byte counts
for every restored Mooncake object and handles incomplete response lists.
The second step packages the complete source over the fixed official native
stack and supplies focused installed-image qualification. Neither step changes
model kernels, dependencies or the sampling policy. Governor is not added;
external PIG remains separately versioned.

CPU development: 150 tests and 11 subtests pass. Final-image, GPU, dual-rail,
real shared KV and production acceptance are separate receipts recorded in
the source Release and deployment repository. CPU success alone is not a
production-readiness claim.
