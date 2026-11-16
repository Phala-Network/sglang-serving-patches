# Official v0.5.23 version maintenance candidate

This is an unpublished complete-version candidate, not an accepted image or a per-model profile.
It preserves the shared v0.5.20 engine main and all older compatibility stacks.
The official base is `297e54fd105e974cdf401e5b4d20253a22c16f90`. Current local complete source candidate `a4d36d4be1df6867b1cbf6517857009d89aed554` has tree `93ca7bb5e66fa212bf7d551fd425ea1ec617d2af`.
Its core predecessor `85e8b30df15fc21a74f01c40cf1d075522348292` is exactly tree-equivalent to frozen B1 core
`902375be759ed3311339c23d30bcef63e464e44f`. The final Qwen parser is included unchanged from
patch `5a2e4eb9dcbc01ebcb2500021ae3ecac0dc2200a97e1596c5b12737110b29413`; its seven-file CPU green passes 300 tests and 122 subtests.
This is not final-image, GPU or production acceptance.

`stack.json` and `series` contain four source-derived steps: shared serving/privacy/lifecycle/
grammar/cache safety and integration, followed by conditionally enabled Qwen policy/model/protocol
adaptations, then the bounded Qwen single-assistant parser. The complete series is required before engine import; intermediate application trees are not
standalone acceptance claims. Shared changes occur once for this official version. No 48/162-step
historical set, Governor hooks, native component or old model profile is copied into this line.

Use the existing verifier from the patch repository root:

```sh
python scripts/stack.py verify --stack-root versions/v0.5.23 --source /path/to/sglang
```

The exact clean-index replay report is recorded separately. Source replay and the existing B1
CPU/GPU evidence do not publish this candidate, qualify a final image, or accept production.
The final engine source/tag/Release binds the real v0.5.23 version-line commit. Engine main owns
recipe/docs; patches main owns this shared version export. Those main commits must be recorded
separately and must never be substituted for the complete engine identity. External PIG is the
only admission controller; embedded Governor is not selected.

The current prepared engine `3923738f25611164d67496bbe3789a78a167c5d1` / tree `68963b8974b65b028f174a222710c75643c11886` adds only version-line CI
metadata after the CPU-qualified parser source above. Both the complete `python/sglang` and
`test` subtrees are identical to `a4d36d4be1df6867b1cbf6517857009d89aed554`; parser patch bytes remain unchanged.
The four-step series uses two workflows: scoped static source checks and the existing Phala
manual full lint. Unrelated upstream hardware, bot and automatic publishing workflows are
retained in official/history refs rather than enabled on this version line. Exact patch replay
uses the existing patches CI job. No workflow has been dispatched for this local candidate.
