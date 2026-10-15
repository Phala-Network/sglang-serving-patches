# Xing request-static EAGLE source candidate

Fixed recipe: TP1, unquantized BF16 weights, E4M3 KV, page64, TRTMLA prefill/decode/draft,
single-layer EAGLE3/topk1/draft4, speculative attention prefill. Default prefill graph remains enabled;
NP12 interval8/chunk8192/default2048/42 buckets/decode full128 is retained for later runtime checks.

Engine `2b9940cb7764c26c40cc8a48538374e7b200dc53`, tree `e0ee5561feb18c56c619f714492da9e93f993156`, is a single logical export of reviewed commit
`30300d021996ceb354ab8fb2b6d09ebf6dc74bcd` with exactly identical bytes. Parent is published native RC5.3 `48e9fc7d56930660999dc108cb5ecddee5245715`.
Step0061 preserves all60 published patch bytes; its source change is13 runtime files,
the existing packaged CPU selector and focused tests. No kernel implementation changes.

Original input plus requested output selects immutable factor64 through262144 and128 through524288;
overflow and pool failure reject without clipping. Existing complete-math cache namespaces and caller
salt remain. Per-profile RoPE scratch adds8 rows, long offset262152, total786448; real frequencies
are unchanged. Q scaling uses the actual long table offset. Target verify and draft extend use fixed4
request blocks; draft steps and graph capture/replay retain model positions without changing physical KV
addresses. Existing decode reserve8/rowheadroom71 and allocator controls remain; no duplicate reserve formula.

Source CPU:17 dedicated cases; affected184pass/10 explicit CUDA skips, no failures/errors.
The corrected original13 tests on RC5.3 yielded12fail/1pass. Independent review found one new
draft-extend plan/main allocator-lifetime gap, now closed with existing record_stream_each.
Final CPU ran after that fix. Duplicate manual Q-scale offset calculation was removed in favor of
the actual rotary table offset. All61 intermediate patch trees actually replay and match.

[DYNAMIC-EAGLE-SOURCE-VERIFICATION.json](DYNAMIC-EAGLE-SOURCE-VERIFICATION.json) binds evidence.
Dynamic image build/publication and CUDA graph/kernel, real512K, mixed cache, quality and recovery
remain separate pending gates. Source/CPU success does not claim dynamic512K serving support.

Step0059 explicitly exports source_range_base `3796ead177e2c344da9e8ca026bf64f32de7f09e` through `5b32c5227da46c3db3f2569aab1d83f81f9d9080`; source_parent records its real immediate parent `585d270714ced0c77656506f49f5c5b955791210`. The existing verifier now supports this optional immutable git-diff ancestor range while retaining default immediate-parent semantics, source-byte binding and every intermediate-tree check. Canonical61-step verification and29 real-Git unit tests pass; a wrong range is rejected. All60 published prefix patch bytes remain unchanged.
