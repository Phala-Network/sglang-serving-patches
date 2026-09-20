# Model selector manifest

The machine-readable selector file is [selectors.json](selectors.json). Each
selector names an exact upstream version, model family, topology, ordered patch
IDs, patch paths and SHA256, plus the immutable fork commit/tree and source
parent. `selected` patches are the only inputs for that
consumer; historical files under a model directory with no selected ID remain
pending source material.

The Kimi selector contains six real v0.5.20 candidate patches and excludes the
chat-close/completed-chunk implementations already represented by shared code.
The Muse selector contains its native channel patch. Nemotron and Gemma
directories preserve real historical source material while their selectors are
pending or empty because their v0.5.19 objects are not replayable against the
maintained v0.5.20 base. DeepSeek lists its complete model patch set; missing
common/native dependencies and the Rust closure keep it blocked.

No selector claims final-image, GPU, model-serving or production acceptance.

The fork commit/tree is authoritative for implementation. These patch files are
deterministic exports for audit and external consumers. A rebase must create a
new immutable fork commit/tree, regenerate its commit-range exports and replay
each selector from the pinned upstream base; a moving branch alone cannot bind
a model build. Old trees, failed replays and evidence remain retained.
