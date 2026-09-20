# Qwen3.8-27B source and patch review index

Official SGLang v0.5.20: 94602c9c2b7cbdb8efd5c52802dac6a1c180089e.

[Full serving source compare](https://github.com/Phala-Network/sglang/compare/94602c9c2b7cbdb8efd5c52802dac6a1c180089e...3c76218a6f3c9621f0cc08af1bf325c7633429ce). Governor hooks are not part of that serving source.

| Repair | Source PR (draft) |
| --- | --- |
| 0001-control-correlation | [Source diff](https://github.com/Phala-Network/sglang/pull/2) |
| 0002-request-cleanup | [Source diff](https://github.com/Phala-Network/sglang/pull/3) |
| 0003-worker-extend-metadata | [Source diff](https://github.com/Phala-Network/sglang/pull/4) |
| 0004-identity-grammar-mask | [Source diff](https://github.com/Phala-Network/sglang/pull/5) |
| 0005-lifecycle-observation | [Source diff](https://github.com/Phala-Network/sglang/pull/6) |
| 0006-parallel-sampling-owners | [Source diff](https://github.com/Phala-Network/sglang/pull/7) |
| 0007-token-auth-redaction | [Source diff](https://github.com/Phala-Network/sglang/pull/8) |
| 0008-schema-normalization | [Source diff](https://github.com/Phala-Network/sglang/pull/9) |
| 0009-schema-argument-coercion | [Source diff](https://github.com/Phala-Network/sglang/pull/10) |
| 0010-xgrammar-schema-rejection | [Source diff](https://github.com/Phala-Network/sglang/pull/11) |
| 0011-allowed-tool-subsets | [Source diff](https://github.com/Phala-Network/sglang/pull/12) |
| 0012-reasoning-visibility-bounds | [Source diff](https://github.com/Phala-Network/sglang/pull/13) |
| 0013-orphan-tool-deltas | [Source diff](https://github.com/Phala-Network/sglang/pull/14) |
| 0014-pre-mm-token-budget | [Source diff](https://github.com/Phala-Network/sglang/pull/15) |
| 0015-image-input-errors | [Source diff](https://github.com/Phala-Network/sglang/pull/16) |
| 0016-watchdog-recovery | [Source diff](https://github.com/Phala-Network/sglang/pull/17) |
| 0017-qwen3_5-template | [Source diff](https://github.com/Phala-Network/sglang/pull/18) |
| 0018-qwen3_coder-parser | [Source diff](https://github.com/Phala-Network/sglang/pull/19) |
| 0019-schema-reference-isolation | [Source diff](https://github.com/Phala-Network/sglang/pull/41) |
| 0020-allowed-tools-output | [Source diff](https://github.com/Phala-Network/sglang/pull/42) |

[Explicit model profile](../profiles/v0.5.20/qwen3.8-27b.yaml) selects 20 repair patches by hash and order. The manifest records exact parent and source commits; the PR stack makes each problem visible as an original-file diff. Draft status is not approval.

[Git verification](validation/serving-git-export-check-r1.json) proves every exported stage reconstructs the complete source commit tree. [No-Governor CPU results](validation/common-no-governor-cpu-r1.json) cover 24 groups with 312 JUnit cases including subtests, zero skips. Four Qwen model groups passed separately; a Governor routing test with a hardcoded source path was corrected and rerun, with the failed evidence preserved.

The initial split preserved the historical 59 files; the current candidate additionally repairs external schema resolution and out-of-subset tool emission. These intentional behavior changes are covered by new red/green tests, not by the older equivalence claim. New composed-image qualification and e4 deployment remain pending. Strict dynamic-platform and model/launch-measurement gaps remain disclosed.

Runtime image publication target: ghcr.io/phala-network/sglang, associated with Phala-Network/sglang. No new immutable image is claimed by this review index.

[Complete engine compare including Governor](https://github.com/Phala-Network/sglang/compare/94602c9c2b7cbdb8efd5c52802dac6a1c180089e...828500b641b57a3e67508aad327397657f8be1f9) is a generated, noneditable review view. The generated view records Governor hook source f9706ed838d472cb20eb468730ef59fbc85f85b8; the runtime Governor component version is independently pinned in the deployment lock; composed engine tree is 0d1590277a2bd6f2f7233b51e7629d0b0988e286. The current engine includes both review fixes; original equivalence evidence remains historical.

The reusable Git-only verifier passed nine boundary tests and the actual 20-patch profile, producing pure serving tree 56f78eb969e50a2eccd8e295d1c6535c7001c00b. The two fixes together passed 40 tests plus 24 subtests; the separate red/green cases and the rejected initial fixture are retained in evidence. CI does not treat these Git checks as human review approval.
