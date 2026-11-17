# Official v0.5.23 version maintenance candidate

This shared version stack preserves the v0.5.20 engine main and all older
compatibility stacks. The official base remains
`297e54fd105e974cdf401e5b4d20253a22c16f90` (v0.5.23).
The complete source successor
[`35f00f8cfaaa56fa3f13edb9e81ae0ae1d4504ed`](https://github.com/Phala-Network/sglang/commit/35f00f8cfaaa56fa3f13edb9e81ae0ae1d4504ed)
has tree `0b2441c7279392ba0dff1e02ec201aa4e6359e37` on
[`codex/sglang-v0.5.23-maintenance`](https://github.com/Phala-Network/sglang/tree/codex/sglang-v0.5.23-maintenance).
It adds a focused nullable-tool repair after the previous complete source
`3923738f25611164d67496bbe3789a78a167c5d1`; no published tag is moved.

`stack.json` and `series` contain five ordered source-derived steps: shared
serving/privacy/lifecycle/grammar/cache safety, conditional Qwen policy/model/
protocol adaptations, the Qwen single-assistant reasoning parser, scoped
version-line CI, and the nullable Qwen XML sentinel repair. Apply the complete
series before engine import; intermediate trees are not independently qualified.
Shared repairs occur once. No historical 48/162-step set or embedded Governor
component is copied into this line; external PIG owns admission.

The fifth step resolves an unquoted XML `null` before the generic mixed-union
string preference only when the original argument schema also accepts null.
Quoted strings, string-only/enum/const constraints, reference scope and the
generic coercion utility keep their existing behavior. The exact changed
module and tests passed isolated CPU red 7 failed/18 passed, then green 25
passed, including stream splits at 1/7/64 characters. This ran in the previous
candidate image's dependency environment with CUDA hidden, no network and no
credentials. It is source-development evidence, not final-image or live API
acceptance. The reasoning parser is unchanged, so its prior CPU evidence
(300 tests and 122 subtests) remains applicable to that unchanged path.

Use the existing verifier from the patch repository root:

```sh
python scripts/stack.py verify --stack-root versions/v0.5.23 --source /path/to/sglang
```

The export workflow checks source-derived patch bytes and clean ordered replay.
The engine's scoped source workflow checks syntax and whitespace; runtime CPU,
GPU, quality and chain checks have separate evidence. No image has been
published and production has not been updated. The final receipt must bind
complete engine source, patches main, recipe main and eventual immutable
source tag/Release/image digest separately. Recipe main is not the complete
v0.5.23 engine identity.
