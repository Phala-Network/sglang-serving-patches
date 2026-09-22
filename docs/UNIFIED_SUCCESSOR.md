# Unified source successor, 2026-09-22

This record does not update the frozen engine428 export, any Governor candidate,
image, CVM or production acceptance. No image build or registry write is needed.

The implementation is Phala-Network/sglang commit
`05a0fe7c11e8262c804b0816328378ddc13beb87`, tree
`3ed4e8e8a04e9a9ac8024b7b6d5dea1a649f32c6`, on navigation branch
`codex/model-union-v0520-20260922`. It combines the three common increments,
six Kimi increments, one Muse increment and the guarded Nemotron literal-token
migration, DS prerequisite/chat source, named-tool schema roots and Qwen complete-call
boundaries. It now adds Muse constraints/channel grammar/history/template wiring,
shared Marlin/BREAKABLE guards and guarded Qwen GGUF loading/vision/prefill.
No common patch bytes were copied. The earlier commit
`6b3ca7eddd1f0a1eed2774bdfd461626c5e0e780` had tree
`b6730c9fe47e14319bb92dc61b8463ae7dcfedfd`, equal to the earlier combined
candidate `83d8dc47ee`. That historical equality is not claimed for the new tree.

`unified-v0520-successor` records the full source range, 57 ordered patch
references, immutable commits and hashes. `export_selectors.py` independently
replays the 31-entry frozen series from official v0.5.20
`94602c9c2b7cbdb8efd5c52802dac6a1c180089e` to tree
`83dcb00885129cc2afefdce2e169ebba697a9a67`, then the successor to the tree above.
The source range is not a Governor v4 release input.

## Current semantic scope

The original 110 per-source records, source hashes, ownership and old evidence
remain in [COVERAGE.json](COVERAGE.json). They describe frozen engine428 and
must not be silently relabeled as successor acceptance.

| Model or family | Present in this successor | Still not established |
| --- | --- | --- |
| Common | llguidance mask callbacks/pinning, typed usage, opt-in mode defaults, stable Marlin route order, NVFP4/MXFP4 FP32 non-atomic reduction and BREAKABLE-only hybrid gate | Linux full runtime imports, Triton/CUDA numerical/capture tests |
| Kimi K3 | Owner identity `1e62ad753c42`, absolute checkpoint grid `9bd58a168358`, prefill sequence cap `6329c4dddd08`, file ownership/prefix `cd0cca6903e8`, chunk guards `5a1799c43d72`, virtual page continuation `02558c2aaab1` | TP8/DCP1/DCP8 runtime and new Governor combination; old CPU/CUDA evidence is scoped to its original source |
| Muse Glimmer | ATEM/JSON framing, required/named schemas, channel grammar, history/default/template propagation; rejection-safe wrapper and counter-based final rollback; 30 CPU tests | External template packaging/license, full model/runtime and cancellation qualification |
| Nemotron 3.5 Lightning | Literal/control tokens with real tokenizer, truncated thought/force-content guards and termination propagation, structured final reserve with filter fail-closed, shared complete-call/XML const execution, native grammar adapter; 19 tokenizer plus 10 termination/budget tests | Unreviewed fusion/Mamba semantics and full model/GPU/runtime qualification |
| DeepSeek V4.1 Flash | DS0001–0026 source and native 19/20 protocol adaptation; connected Vision/Engram/Python C1/C2 consumers, guarded quantization/indexer/communication, DS-only async, media checks, integer effort and both tool-none carriers; 38 focused plus 10 chat CPU tests | Native extensions/ABI, weights, GPU/numerical behavior, real HiCache/Mooncake ACK/reload and model acceptance |
| Gemma 4 26B A4B | Common source; historical fork `d0b3e70cbc5ed3cc757d22e79ffa1fff28f58571` remains identifiable | Shared old image does not prove a Gemma-specific increment or qualify Qwen GGUF paths |
| Qwen3.8 27B / Qwen3.5 GGUF | Complete-call atomic publication; guarded name/head/layout/BF16/shared-identity completeness and vision projector loading; Qwen-only BF16/Q8_0 CUDA prefill dispatch | Full model loading and CUDA numerical/performance tests; CPU fixtures do not qualify kernels or weights |
| Qwen3.6 27B | Common template, effort/history/schema paths and selected union1 native required/empty-XML checks; historical fork retained | Full template/model/runtime and final-image acceptance |
| Qwen2.5 7B | Common source only | Do not infer Qwen3.5/GGUF applicability from shared historical image |
| GLM 5.3 | Existing frozen nine logical changes and formatting correction unchanged | No new GPU or Governor-on-GLM acceptance |

Current source paths are the exact paths in each exported source delta.
Key boundaries are `entrypoints/openai/serving_chat.py`,
`parser/reasoning_parser.py`, `function_call/muse_glimmer_detector.py`,
`managers/tokenizer_manager.py`, `managers/schedule_policy.py`,
`mem_cache/hicache_storage.py`, and `model_executor/runner/prefill_cuda_graph_runner.py`
under `python/sglang/srt`.

## Verification

- The current integration receipt is `UNION_SOURCE_VALIDATION_20260922.md` in
  the engine tree. It records Muse30/0skip, Nemotron19/0skip plus 10 focused
  termination/budget tests, Qwen complete-call17 including const, DeepSeek
  encoder8/source-method16/MXFP4loader3/chat10/sharedprotocol11, and nearby
  Qwenhistory5/Marlin6/HiCache13 (one Gloo skip). Older counts below retain
  their historical scope rather than being rewritten as reruns.
- The single native dependency `xgrammar==0.2.6+phala.union1` passed 655
  installed native tests and 14 installed adapter tests without skips.
  `external-dependencies.json` and the deterministic delta reproduce complete
  tree `b8dcb87b50b99cc61dbab46e7dcfbd34f78a2f45` from public upstream.
  Engine recipe `--verify-only` independently fetched that base and verified
  tree, license and DLPack URL/gitlink. No wheel or runtime image was rebuilt.
  The wheel is a local tested artifact, not publicly installable from PyPI;
  native candidate commits are local provenance, not invented public refs.
- Nine real-Git export fixtures now pass, including external native replay
  and negative tree/license cases. The final source and external native tree
  are actually replayed; the manifest alone is not proof.
- Four exact selector replays passed, including the combined successor.
- The historical DeepSeek selector retains its expected failure at raw DS0011
  after ten applications. The new combined selector replays the adapted source;
  this does not turn the historical failed selector into acceptance.
- DS chat migration: 10 CPU tests. Named-tool schema-root preservation: 5 CPU
  tests. Qwen/Gemma source-method audit: 5 CPU tests. Qwen complete-call suite:
  16 tests; boundary probe now 4/4 (previous three real failures are retained in
  source history). These tests do not run a full serving import.
- `qwen3_coder`, `step3p5` and `nanbeige` all register the same detector directly.
  No subclasses were found; the no-argument constructor and parser's stream,
  nonstream and finish delegation remain compatible. Atomic publication changes
  all three selectors, not only Qwen. Step/Nanbeige models and SSE are untested.
- DS shared allreduce/PTX/FP8 changes are not all DS-guarded. Non-DS runtime
  regressions and the new block32 FP8 path remain unqualified. An offline Rust
  check failed before compilation because cached `prost` was absent; it is not
  ABI evidence. The later DS0015 integration connects actual model forward,
  weight remapping/loading, Engram history and C1/C2 backup/load/prefetch paths;
  CPU source-method tests are not native transfer or GPU evidence.
- Reference-only selectors verify immutable identity but report `passed: null`.
- Seven real-Git fixture regressions passed: moved/deleted navigation refs,
  reference-only evidence, corrupt baseline bytes, wrong tree, unverified base,
  expected failure retention and invalid replay mode.
- Muse suite: 28 CPU cases, zero skips with the pinned template. Three tests
  execute actual `_process_messages` → `_apply_jinja_template` → render/encode
  methods, with real Jinja rendering and a test tokenizer. Other cases execute
  real schema/parser/grammar/protocol source; inner grammar and media are doubles.
  Without the template input, its three tests explicitly skip.
- External Muse template SHA256:
  `900db3effc316e33295ec3d7dfa2df83ea2735228cba73adba8fecc2e83343f7`,
  matched to immutable Compose `2e16dfd8ab1b433e549fb1dc7cdd200dbd326bbd`.
  The source migration record is `docs/validation/MUSE_SOURCE_MIGRATION_20260922.md`
  in the engine fork. No template bytes were redistributed into this repository.
  A standalone template license was not found; packaging/redistribution remains
  a separate gate rather than inventing an Apache grant for that artifact.
- Marlin/BREAKABLE: 6 dependency-free source tests. Both FP4 formats retain FP32
  scratch reduction; non-Marlin/default dispatch and non-BREAKABLE GQA gates remain.
  Scalar Triton fixtures do not establish actual kernel compilation or numerics.
- Qwen GGUF correctness: 20 tests with real CPU tensors, GGUF reader/writer,
  Transformers meta mapping and actual source-method loader chain. Q8 prefill:
  11 source-dispatch tests; simulated CUDA/device/kernel metadata, not GPU speed.
  Tested torch2.13.0/transformers5.12.1/tokenizers0.22.2 match source pins;
  gguf0.19.0 and numpy2.5.3 are unpinned test inputs. Historical kernel0.4.6.post1
  versus source0.4.7 has no loaded-extension acceptance here.
- Linux export CI passed on workflow fix `d175bcc22f0e52ccf12051758b9554d943bddcab`,
  run `35727054057`; the earlier invalid-context run `35726737708` is retained.
- Nemotron default dependency-light source-method suite: 9 tests pass, real
  artifact class explicitly skipped when its input is absent. The separate
  artifact-enabled run passed 19 tests with zero skips, including 4 real-BPE
  tests and 6 inherited boundary tests in the artifact class.
- Real artifact: `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4` revision
  `cc84af2fe71647d87f4486c064f320e1e7535243`, `tokenizer.json` SHA256
  `623c34567aebb18582765289fbe23d901c62704d6518d71866e0e58db892b5b7`,
  17,077,484 bytes, tested with tokenizers 0.22.1. Marker IDs 12/13/14/15 all
  have `special=false`; default skip-special decoding preserves them.
  Real tests cover ordinary-BPE literal prompts, Unicode split bytes,
  cumulative/incremental output IDs, and a real end-token preceding split text.
  Metadata was copied read-only from the existing pinned development cache;
  no weights, services, containers or routes were changed.
- No Linux full runtime imports, GPU, final-image or production tests were run
  here. The default local interpreter does not carry the serving stack; the
  isolated `tmp/qwen-gguf-cpu-deps-20260922` environment does contain real
  torch2.13.0/transformers5.12.1 used by the 31 GGUF tests above. Source-method,
  CPU tensors and real-tokenizer tests cannot replace those gates.
- Candidate CI/lint repair `a6bfd34af1` removes inherited automatic GPU/vendor,
  release and robot triggers while preserving manual/reusable workflow bodies.
  One PR-only source check runs real Python/config/registry lint and selected
  CPU tests. Full upstream lint remains manual. Default-branch automation
  cannot be disabled by this candidate branch. Old lint failure35729558772 is
  retained; it exposed real format errors, missing dynamic class/json bindings
  and a watchdog test entrypoint omission, all repaired in source.
- After lint repair: Muse28/0skip, Nemotron19/0skip, DSchat10, Qwencomplete16,
  Qwenhistory5, commonMarlin6 and GGUF20+11 pass again. HiCache source tests
  pass13 with the real Gloo test explicitly skipped. Unregistered historical
  tests moved from `test/registered/unit` to `test/manual/unit` at the same
  relative depth; full-runtime and native-grammar tests are not represented
  as lightweight checks.

Run `python -m unittest discover -s tests -v` and
`python scripts/export_selectors.py --source /path/to/sglang --check`.
The main frozen export remains independently checked by `scripts/export.py`.
No additional per-model workflow or long-lived profile was added.

## Remaining historical semantics

Muse's nine source contracts are now migrated or reuse current shared behavior;
the source record maps each exact historical commit. Native grammar, image
template binding/license and cancellation acceptance remain separate.
Nemotron now includes native tools/order adapter checks, truncated-thought
termination guards, shared complete streaming calls, structured final budget
and XML const-type migration. This does not close unreviewed MoE fusion or
Mamba/admission semantics. Marlin/FP32 and guarded BREAKABLE source
migration is integrated by `fa291d652a` (donor `6281c5dcdd`); it still lacks
Triton/CUDA numerical and capture acceptance. Page alignment is integrated in
the shared Kimi checkpoint path, not separately model-qualified.
Deferred metadata `12593d20ead3` retains its upstream-coverage
proof rather than being duplicated. Old Goodput 0.714982 below 0.7338 was an
override, not a pass.

Qwen GGUF historical `5404f7600755`, `d67e821bd5ea`, `2b2584575aa5` and
type-gated optimization `c4afa9828243` are now adapted in guarded source paths,
separate from full-model/kernel acceptance. Gemma4 FP8 and Qwen2.5 FP8 sharing an old image does not
qualify either model. The selected XGrammar dependency reconciles tested historical
0.2.1 (`5b4e9ce9e72524037ae24ecd831b9b6604d2eb48`) and 0.2.6
(`bc09a30ec10ba30a6c1ab0c79eaeba3ca518d11f`) semantics in one union1 build.
Its native CPU correctness does not establish a full engine image or GPU result.
