# Model selector manifest

The machine-readable selector file is [selectors.json](selectors.json). Each
selector names an exact upstream version, model family, topology, ordered patch
IDs, patch paths and SHA256, plus the immutable fork commit/tree and source
parent. `selected` patches are the only inputs for that
consumer; historical files under a model directory with no selected ID remain
pending source material.

The shared v0.5.20 successor baseline contains three common increments exactly
once. Kimi selects that baseline plus six Kimi-guarded patches and excludes the
chat-close/completed-chunk implementations already represented by shared code.
Muse selects the same baseline plus its native channel patch. Both selectors
reproduce exact immutable fork trees from engine 428. Nemotron, Gemma and the
historical Qwen deployments bind extant v0.5.19 fork branch tips and trees, but
remain pending migration rather than pretending to be v0.5.20 selections.
The historical DeepSeek selector lists its model patch set and preserves its
expected raw-DS0011 replay failure. The unified successor separately contains
DS0001–0010 prerequisites and adapted DS0011; missing remaining source closure,
native ABI and model-forward/cache consumption keep model acceptance blocked.

Run `scripts/export_selectors.py --source /path/to/sglang --check` before using
a selector. The check verifies the immutable commit and tree, regenerates
source-backed patch bytes, checks every SHA256, replays the complete frozen
series from its official base, and then cleanly replays exact successor
selectors in a temporary Git index. Branches are navigation aids and may move
or be archived without invalidating immutable evidence. Reference-only results
have `passed: null`, not a replay pass.

`unified-v0520-successor` combines the existing common, Kimi and Muse increments
with guarded Nemotron literal-token boundaries, DS prerequisites/chat encoding,
named-tool schema roots and Qwen complete-call boundaries in a single source tree.
Further unified increments restore Muse constraint/grammar/history/template
call-chain semantics, common Marlin/BREAKABLE guards and Qwen-scoped GGUF
loading/vision/prefill. Exact CPU evidence does not replace native/kernel or
external-template packaging acceptance.
The latter also affects `step3p5` and `nanbeige`, which use the same detector;
their model behavior has not been qualified.
The ordered range and exact limitations
are recorded in [UNIFIED_SUCCESSOR.md](docs/UNIFIED_SUCCESSOR.md).

No selector claims final-image, GPU, model-serving or production acceptance.

The fork commit/tree is authoritative for implementation. These patch files are
deterministic exports for audit and external consumers. A rebase must create a
new immutable fork commit/tree, regenerate its commit-range exports and replay
each selector from the pinned upstream base; a moving branch alone cannot bind
a model build. Old trees, failed replays and evidence remain retained.
