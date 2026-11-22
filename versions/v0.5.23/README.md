# SGLang v0.5.23 maintenance

The version stack starts from official SGLang `297e54fd105e974cdf401e5b4d20253a22c16f90`.
The complete engine is maintained on `codex/sglang-v0.5.23-maintenance`. The
current commit and tree are pinned in [stack.json](stack.json). External PIG
owns admission on this version line.

The first five entries produced
[phala-v0.5.23-1](https://github.com/Phala-Network/sglang/releases/tag/phala-v0.5.23-1).
The sixth keeps BF16 queries in compatible SM103 generation while continuing
to store E4M3 K/V. It covers single-token decode, fixed-width speculative
verify and draft extend, and the decode tail of mixed batches. Context
prefill uses E4M3 queries. The seventh entry adds the pinned-base release
recipe and its final-image checks.

Apply [series](series) in order. Use the exporter to verify exact patch bytes
and complete tree replay.

```sh
python scripts/stack.py verify --stack-root versions/v0.5.23 --source /path/to/sglang
```

The source release records the immutable engine and image identities with
their verification results.
