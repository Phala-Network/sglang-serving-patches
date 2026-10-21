# Kimi model-level checkpoint cache release

This optional common loader repair extends the existing ref5/DFlash-mask
maintenance stack by one patch; all32 previous patch bytes are unchanged.
The complete33-step replay matches the runtime tree in
[the source receipt](source-verification.k3protocol3-ref5-modelcache1.json).

It adapts [upstream PR40594](https://github.com/sgl-project/sglang/pull/40594)
through `model-loader-extra-config`, preserving the public boolean shard flag.
Default loading remains unchanged. Model mode coordinates CUDA copies and
rank completion before advising checkpoint file-cache release, and excludes
unsupported loaders and startup overlap. No serving kernel or dependency changes.

34 focused tests pass on the final image without runtime source mounts;
the real two-rank CPU/Gloo file-cache experiment passes. These do not establish
full Kimi CUDA/TP8 cold-start pressure or throughput improvements. See the
immutable engine release and its recipe for configuration and limitations.

## Optional bounded TP batches (modelcache2)

The additive common patch0034 introduces `checkpoint_cache_batch_shards` (zero
by default). It requires the ordinary buffered mmap loader, model-end release,
single-node TP-only ranks, Gloo and no checkpoint prefetch. Ranks agree on
file identity/order, then synchronize CUDA copies and exchange live mappings
before advising completed files. Retained references defer release. New
collectives use bounded waits. No serving code or dependency changes.

The preceding33 patch files are unchanged. All34 intermediate source trees
replay exactly. Qualification includes41 final-image unit tests and11 real
two-process CPU/Gloo scenarios. CPU results do not establish CUDA/TP8 full-model
pressure or performance. See the modelcache2 immutable engine release and
`source-verification.k3protocol3-ref5-modelcache2.json` for identities.
