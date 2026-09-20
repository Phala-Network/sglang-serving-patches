# Qwen3.8-27B source and patch review index

Official SGLang v0.5.20: 94602c9c2b7cbdb8efd5c52802dac6a1c180089e.

[Full serving source compare](https://github.com/Phala-Network/sglang/compare/94602c9c2b7cbdb8efd5c52802dac6a1c180089e...514fcaf8c5a605a58ebb2f9dc1cc743e4a79b836). Governor hooks are not part of that serving source.

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

[Explicit model profile](../profiles/v0.5.20/qwen3.8-27b.yaml) selects all 18 repair patches by hash and order. The manifest records exact parent and source commits; the PR stack makes each problem visible as an original-file diff. Draft status is not approval.

[Git verification](validation/serving-git-export-check-r1.json) proves every exported stage reconstructs the complete source commit tree. [No-Governor CPU results](validation/common-no-governor-cpu-r1.json) cover 24 groups with 312 JUnit cases including subtests, zero skips. Four Qwen model groups passed separately; a Governor routing test with a hardcoded source path was corrected and rerun, with the failed evidence preserved.

The historical 59-file source behavior remains unchanged; the source chain additionally places the already-tested generic correlation regression in SGLang. New composed-image qualification and e4 deployment remain pending. Strict dynamic-platform and model/launch-measurement gaps remain disclosed.

Runtime image publication target: ghcr.io/phala-network/sglang, associated with Phala-Network/sglang. No new immutable image is claimed by this review index.

[Complete engine compare including Governor](https://github.com/Phala-Network/sglang/compare/94602c9c2b7cbdb8efd5c52802dac6a1c180089e...cb88b5675f50a26090407f2dc155de8bdd0e42fd) is a generated, noneditable review view. Governor source is 42f3ac9d25faa72d6dba66969eaec23097f4e2bd; composed engine tree is d2b5d9abb5487f644b7a71e18b9caa9cce9b71d1. All 59 historical file blobs match exactly; the only additional source file is the generic correlation regression.
