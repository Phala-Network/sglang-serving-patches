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
DeepSeek lists its complete model patch set; the expected replay failure and
missing native closure/ABI keep it blocked.

Run `scripts/export_selectors.py --source /path/to/sglang --check` before using
a selector. The check verifies the immutable commit and tree, regenerates
source-backed patch bytes, checks every SHA256, replays the complete frozen
series from its official base, and then cleanly replays exact successor
selectors in a temporary Git index. Branches are navigation aids and may move
or be archived without invalidating immutable evidence. Reference-only results
have `passed: null`, not a replay pass.

`unified-v0520-successor` combines the existing common, Kimi and Muse increments
with guarded Nemotron literal-token boundaries in a single source tree.
The ordered range and exact limitations
are recorded in [UNIFIED_SUCCESSOR.md](docs/UNIFIED_SUCCESSOR.md).

No selector claims final-image, GPU, model-serving or production acceptance.

The fork commit/tree is authoritative for implementation. These patch files are
deterministic exports for audit and external consumers. A rebase must create a
new immutable fork commit/tree, regenerate its commit-range exports and replay
each selector from the pinned upstream base; a moving branch alone cannot bind
a model build. Old trees, failed replays and evidence remain retained.
