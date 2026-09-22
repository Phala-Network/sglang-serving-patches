# Model selector manifest

The machine-readable selector file is [selectors.json](selectors.json). Each
selector names an exact upstream version, model family, topology, ordered patch
IDs, patch paths and SHA256, plus the immutable fork commit/tree and source
parent. `selected` patches are the only inputs for that
consumer; historical files under a model directory with no selected ID remain
pending source material.

The active complete-source selector is `unified-v0520-successor`: engine
`228f7d93dc7ab0f5b08bc714eb5d4a29afc01d33`, tree
`0af2ff1dbe241285caacf8e8236c918a434b9889`.
It cleanly replays the protected 31-step engine428 baseline and 59 successor
patches. Common fixes occur once with model-specific guards.

Older Kimi/Muse selectors are historical partial-source checkpoints.
Nemotron, Gemma and historical Qwen reference selectors retain their v0.5.19
identities without claiming v0.5.20 replay. The raw historical DeepSeek selector
retains its expected DS0011 failure; that does not describe current adapted
DS0001–0026, whose Vision/Engram/Python C1/C2 consumers are connected.

Run `scripts/export_selectors.py --source /path/to/sglang --check` before using
a selector. The check verifies the immutable commit and tree, regenerates
source-backed patch bytes, checks every SHA256, replays the complete frozen
series from its official base, and then cleanly replays exact successor
selectors in a temporary Git index. Branches are navigation aids and may move
or be archived without invalidating immutable evidence. Reference-only results
have `passed: null`, not a replay pass.

The unified tree combines common, Kimi, Muse, Nemotron, DS0001–0026/native DS
protocol, Qwen GGUF/vision/prefill, GLM and shared Marlin/BREAKABLE/parser
changes, with one separately pinned XGrammar union1 dependency.
[Successor coverage](docs/SUCCESSOR_COVERAGE_20260922.json) maps all 110 source
records: 104 source-covered, six upstream-covered. Checkpoint defaults/GDN
layout are mapped; fusion/Mamba audit is closed; malformed weight-update and
initial SSE error status residuals are repaired.
Exact CPU evidence does not replace native ABI, GPU/model or external-template
packaging acceptance.
The shared detector also affects `step3p5` and `nanbeige`;
their model behavior has not been qualified.
The ordered range and exact limitations
are recorded in [UNIFIED_SUCCESSOR.md](docs/UNIFIED_SUCCESSOR.md).

No selector claims final-image, GPU, model-serving or production acceptance.

The fork commit/tree is authoritative for implementation. These patch files are
deterministic exports for audit and external consumers. A rebase must create a
new immutable fork commit/tree, regenerate its commit-range exports and replay
each selector from the pinned upstream base; a moving branch alone cannot bind
a model build. Old trees, failed replays and evidence remain retained.
