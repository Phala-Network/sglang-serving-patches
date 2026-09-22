# Unified source successor, 2026-09-22

This record does not update the frozen engine428 export, any Governor candidate,
image, CVM or production acceptance. No image build or registry write is needed.

The implementation is Phala-Network/sglang commit
`6acf476ccf453e5545be9b12353b67fe09cdbf4c`, tree
`4913ef5c124fbbfb169c74fc714b64def9f4ba8b`, on navigation branch
`codex/model-union-v0520-20260922`. It combines the three common increments,
six Kimi increments, one Muse increment and the guarded Nemotron literal-token
migration. No common patch bytes were copied. The preceding commit
`6b3ca7eddd1f0a1eed2774bdfd461626c5e0e780` had tree
`b6730c9fe47e14319bb92dc61b8463ae7dcfedfd`, equal to the earlier combined
candidate `83d8dc47ee`. That historical equality is not claimed for the new tree.

`unified-v0520-successor` records the full source range, ten ordered patch
references plus the Nemotron migration, immutable commits and hashes. `export_selectors.py` independently
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
| Common | llguidance mask callbacks/pinning `87ace709c88e`, typed usage `89f583819b2f`, opt-in mode defaults `1db913dd7b38` | Linux package/import and combined runtime tests |
| Kimi K3 | Owner identity `1e62ad753c42`, absolute checkpoint grid `9bd58a168358`, prefill sequence cap `6329c4dddd08`, file ownership/prefix `cd0cca6903e8`, chunk guards `5a1799c43d72`, virtual page continuation `02558c2aaab1` | TP8/DCP1/DCP8 runtime and new Governor combination; old CPU/CUDA evidence is scoped to its original source |
| Muse Glimmer | Required tool native channel delta `6b3ca7eddd1f`; Gumbel/deferred-Mamba upstream coverage retains its original proof | Historical template/cardinality/grammar/cancellation deltas are not all proven equivalent by this one parser patch |
| Nemotron 3.5 Lightning | Literal/control-token source `4dbfdf98a4d5` adapted in `6acf476ccf45`: prompt helper, token-ID propagation, model/template guard and current parser methods; 19 CPU tests with real pinned tokenizer | Historical missing-closer fallback, complete tool/schema contracts, Marlin/FP32 and BREAKABLE graph history remain separately pending; no model/GPU acceptance |
| DeepSeek V4.1 Flash | Frozen common behavior only | Native closure selector still fails at `dsv41-0011-chat-encoding.patch`, after ten successful applications. Complete native ABI/recipe and model protocol guards remain mandatory |
| Gemma 4 26B A4B | Common source; historical fork `d0b3e70cbc5ed3cc757d22e79ffa1fff28f58571` remains identifiable | Shared old image does not prove a Gemma-specific increment or qualify Qwen GGUF paths |
| Qwen3.8 27B / Qwen3.5 GGUF | Current guarded Qwen/common implementation plus mode sampling defaults | Historical GGUF load, vision and Q8_0 source records still require semantic and hardware review |
| Qwen3.6 27B | Current common template, effort/history/schema/media paths; historical fork `711978779936d1918d038de8515e33f968cb5193` retained | Native XGrammar version/required/XML equivalence is not established by source export |
| Qwen2.5 7B | Common source only | Do not infer Qwen3.5/GGUF applicability from shared historical image |
| GLM 5.3 | Existing frozen nine logical changes and formatting correction unchanged | No new GPU or Governor-on-GLM acceptance |

Current source paths are the exact paths in each exported source delta.
Key boundaries are `entrypoints/openai/serving_chat.py`,
`parser/reasoning_parser.py`, `function_call/muse_glimmer_detector.py`,
`managers/tokenizer_manager.py`, `managers/schedule_policy.py`,
`mem_cache/hicache_storage.py`, and `model_executor/runner/prefill_cuda_graph_runner.py`
under `python/sglang/srt`.

## Verification

- Four exact selector replays passed, including the combined successor.
- DeepSeek retained its expected failure; it did not become a pass.
- Reference-only selectors verify immutable identity but report `passed: null`.
- Seven real-Git fixture regressions passed: moved/deleted navigation refs,
  reference-only evidence, corrupt baseline bytes, wrong tree, unverified base,
  expected failure retention and invalid replay mode.
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
  here. The local Python still has no torch or transformers. Source-method
  and real-tokenizer tests cannot replace those gates.

Run `python -m unittest discover -s tests -v` and
`python scripts/export_selectors.py --source /path/to/sglang --check`.
The main frozen export remains independently checked by `scripts/export.py`.
No additional per-model workflow or long-lived profile was added.
