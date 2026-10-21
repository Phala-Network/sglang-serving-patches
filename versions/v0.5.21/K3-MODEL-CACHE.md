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
