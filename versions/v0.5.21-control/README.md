# Frozen SGLang 0.5.21 control maintenance

This candidate preserves the user-fixed Phala control release and adds upstream
[DSPARK #42987](https://github.com/sgl-project/sglang/pull/42987): AUTO folded
proposal sampling may use a sharded head when its existing memory budget passes.
OFF, FORCE, sampling math, gamma and eager fallback are unchanged.

This is a compatibility maintenance exception to release-from-main in the engine
repository, following its existing `phala/v0.5.21-control` release. It is required
for the frozen control comparison; it is not a new per-model full-stack policy.
Shared 0.5.20 and the separate Kimi 0.5.21 maintenance stack remain intact and are
not inputs to this engine. The patch repository may integrate this directory on
its shared main without applying the unrelated stacks to the engine.

Apply [series](series) relative to this directory on the official base recorded
in [manifest.json](manifest.json). The first export contains the existing control
runtime delta exactly once; the second contains only the sampler and its upstream
resolver test. The complete source of truth is
[Phala-Network/sglang](https://github.com/Phala-Network/sglang), candidate commit
`63f53d18d3d5d7dbfee189c0ed8e2ac10c05407f` (local candidate until publication).
Both files are deterministic full-index Git exports of the recorded parent and
commit. Export-format hashes differ from the original upstream patch; the applied
source bytes are identical.

The original control contains a `phala/` packaging archive, including duplicate
installed snapshots. That archive is neither a runtime delta nor copied into this
patch repository. Replaying both exports produces `runtime_tree_without_phala`.
To reproduce the exact full engine tree in a temporary Git index, read the
manifest base, apply the first export with `git apply --cached`, restore the
unchanged archive with `git read-tree --prefix=phala/ <control_commit>:phala`,
then apply the second export. `git write-tree` must equal `engine_tree`.
The two intermediate control and final candidate full trees were actually checked.
The inherited control export retains its existing blank line at EOF; no baseline
whitespace cleanup is mixed into this change.

No dependency, HF CLI, embedded Governor, external PIG or native component change
is selected. Development evidence: CPU selector checks, five GPU numeric cases,
and 63 synthetic TP2 graph replays passed. Real-model branch/protocol/resource
qualification and performance comparison are separate gates and are not claimed
by source replay. No diagnostic instrumentation is present in this candidate.
Final image qualification must use the immutable built image without source mounts.

## Independent dequant memo candidate

`series.dequant-memo` / `manifest.dequant-memo.json` reuse the same original control export and add only the safe two-file dequant memo change. This is an alternative experiment on the same fixed baseline, not a combination with DSPARK. Engine `06fd87ff10e911dc8fc27296fb2b5fc5212eb529` is local-only; GPU/model/performance acceptance is pending. Actual temporary-index replay reproduces its complete tree. The existing DSPARK series is unchanged.

Independent reasoning usage correction: `series.reasoning-usage` and
`manifest.reasoning-usage.json` preserve frozen control and count only newly
retained tokens after finish resolution. Source CPU tests cover 13 cases;
this is accounting repair, not a performance result.

Independent FP8 direct-read #43498: `series.direct-read43498` and
`manifest.direct-read43498.json`; complete shared-memory guard and eager
long-prefix routing on control. No GPU/native fallback qualification yet.
