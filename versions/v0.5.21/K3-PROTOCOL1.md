# K3 protocol compatibility release

Source tag [`phala-v0.5.21-3-k3protocol1`](https://github.com/Phala-Network/sglang/releases/tag/phala-v0.5.21-3-k3protocol1)
binds complete engine `350852e6b384c1881431b0e8ec59e73cd5be3107`, tree
`ef9cef2c85ab76e55e5d49d43cc2359a21addf30`. It preserves the deployed
mcfix3 engine `e9a40ece22f8539d434ccc138336019ddbf2e06c` and adds the qualified
K3 protocol implementation `dfbdb81c0711575763d5ed26d04b0dd7e498faf0` plus
build metadata and exact tested-byte packaging.

The [release record](releases/phala-v0.5.21-3-k3protocol1.json) and
[ordered series](series.k3protocol1) reference the same canonical first eight
patches as the existing v0.5.21 line, followed by six source-derived protocol
commits and one packaging commit. They do not copy a model-specific patch
collection. Existing 49-step GGUF `stack.json`/`series`, shared v0.5.20 main,
and their source identities remain unchanged. The existing v0.5.21 compatibility
release exception applies: its official/native/Governor contract differs from
shared v0.5.20 main. The deployed base remains the input for this repair.

The [existing stack verifier's replay receipt](source-verification.k3protocol1.json)
records actual clean-index application of all 15 patches from official
v0.5.21 `e00930c5489053f26d86b179cee0d087f846acbb`, source-export byte checks,
every intermediate tree, and the exact complete final tree. The final commit
stores all eight product blobs at their qualified hashes: seven CRLF files and
the new LF encoding module. Only line endings differ from the development
commit's clean-filtered blobs; Python implementation is unchanged.

The repair retains native grammar ownership through thinking/tool/response
boundaries, preserves JSON-string tool values and history, validates strict
final output, rejects unsupported schema roots, and removes full accepted-token
history copying during rollback. The identical product bytes and p1 dependency
passed 809 CPU tests with 782 subtests, 48 HTTP cases and a 60-case direct-backend
live matrix. Twelve synthetic-tokenizer skips remain; real-tokenizer counterparts
ran. These source/candidate checks do not replace final-image/public/PIG or
per-node production acceptance. No E2E throughput improvement is claimed.

Dependency `xgrammar==0.2.6rc2+phala.ecmadot.20261014.p1` is the already tested
CPython 3.12 Linux wheel, SHA256
`e80259e5837dd5f8c21cac0b95906def48b59bcb27705697733d438ce7acd36b`.
The source Release provides that wheel; the engine-owned
[build directory](https://github.com/Phala-Network/sglang/tree/350852e6b384c1881431b0e8ec59e73cd5be3107/docker/phala/kimi-protocol1)
keeps its original three dependency deltas and exact provenance. The image uses
the existing wheel without rebuilding it. Global union1 dependency metadata is
not changed by this compatibility release. Mooncake, external PIG, model,
concurrency, memory and routing remain the deployed configuration's responsibility.

Loose tools preserve their existing contract. Unsupported root combinations and
dependency constraints return explicit 400s; this release does not promise
complete JSON Schema support or measured natural-traffic tool success gains.
Final image digest and deployment outcomes belong in the source Release receipt.
