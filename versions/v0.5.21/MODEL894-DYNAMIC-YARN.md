# Qwen GGUF request-static YaRN

The phala-v0.5.21-7 release uses the published phala-v0.5.21-6 source and its
unchanged 46-step prefix. Steps 47-49 add GGUF nested configuration, packed-weight
and embedding/vision loading, conservative large-prefill dispatch, and
engine-owned incremental packaging plus the combined config regression.

Complete engine: `c2ce5382dad45fd85e39f5d4e1d93165225eb34d`; complete tree:
`c3ac2ba255436604bb219d9fa798610d8697a542`. The original tested build input is
patches `90adf120aa19e683f95d8702c89e31fb1c3d4ab0`. Release metadata synchronizes
the canonical stack to all 49 patches without changing their bytes or series.
Source replay uses the standard command from this repository:

```sh
python scripts/stack.py verify --stack-root versions/v0.5.21 --source /path/to/sglang
```

The [engine recipe](https://github.com/Phala-Network/sglang/blob/c2ce5382dad45fd85e39f5d4e1d93165225eb34d/docker/phala-model894-yarn/Dockerfile)
installs 13 GGUF runtime modules over the fixed released base, with preimage
guards and wheel RECORD updates. Native libraries and dependencies are retained.
The tested local image config ID is
`sha256:c8bd826b1f1227c827d6906fb0148a8c7622d2fde4da72b9e9945bd4f09532d1`.
The [published engine Release](https://github.com/Phala-Network/sglang/releases/tag/phala-v0.5.21-7)
owns the immutable registry digest after publication. Its inherited OCI version
label remains phala-v0.5.21-6; engine and original patch revision labels identify
the tested source. No embedded Governor is selected.

Qualified scope is the same Q8_0/BF16/F32 GGUF and BF16 mmproj revision
`993a5971fda8f30dd1b7eb2654792ba4415c7460`, tokenizer/processor Qwen/Qwen3.8-27B-FP8
revision `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`, FA3, FP8 E4M3 KV and no
MTP/speculation. Context1048576 requires the full nested YaRN map (theta10000000,
partial0.25, MRoPE sections11/11/10 and interleavedtrue), original context262144,
factor4 and request-static factors1/2/4, with the longer-context opt-in.

Automatic selection uses the expanded prompt plus original declared output
budget. Explicit factors use `custom_params.yarn_factor`. Chat omitted/null
output budget selects4; a finite output budget lets a short prompt select1.
The1M cap is total context, not pure input. At tested prompt1048320 plus
declared256, admission selects4 while effective output capacity is254; observed
output stopped naturally at27 tokens. Real cap+1 and short recovery passed.

The fixed35 structured-output bodies scored32/35 in initial dynamic, cleared
dynamic and cleared same-image native1, with all35 complete choices/usage
identical across all three rounds. Cases22/28/32 reached2000 tokens with unclosed
JSON and are disclosed shared failures. Tests qualify scoped functionality and
limited long-input retrieval, not all-model quality, throughput or concurrency
capacity. GGUF Weight Cache Daemon IPC remains unsupported/off. Use passive
`/ready` for readiness rather than a generating probe during long prefill.
Image publication and production service acceptance remain separate stages.
