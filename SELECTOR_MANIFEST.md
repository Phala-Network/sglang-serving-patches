# Model selector manifest

The machine-readable selector file is [selectors.json](selectors.json). Each
selector names an exact upstream version, model family, topology, ordered patch
IDs, patch paths and SHA256. `selected` patches are the only inputs for that
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
