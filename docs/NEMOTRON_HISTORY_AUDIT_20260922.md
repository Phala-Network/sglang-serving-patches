# Nemotron fusion and Mamba historical source reconciliation

Audited 2026-09-22 against engine
`05a0fe7c11e8262c804b0816328378ddc13beb87`, tree
`3ed4e8e8a04e9a9ac8024b7b6d5dea1a649f32c6`, with fixed official v0.5.20
baseline `94602c9c2b7cbdb8efd5c52802dac6a1c180089e`.
No engine changes, new feature, image build, GPU work or deployment resulted.
Frozen predecessor coverage records are intentionally not rewritten as successor
runtime acceptance.

## Exact upstream coverage

Each upstream commit below was checked with `git merge-base --is-ancestor`
against the fixed official baseline (all exit 0), not merely found by subject.

| Historical patch | Upstream baseline ancestor | Disposition |
| --- | --- | --- |
| `65a1b3f10fd08d8330384708723d215fbd343b65` | `214313ee796b804cb4191dfacfade4af9cf602f3` (#30430) | Latent projection/shared add retained |
| `752cbf71d2fc874d79f0de511265209e15a2ed0f` | `0b57847ebfd4e28a2c371892b9d4ac778e34b3fa` (#37836) | Flat Mamba2 SSM indexing/recomputation retained |
| `72d09f13ce3e931800377c191eb1724a30c55e0e` | `e4adf63275005f4b3e6f8d74ae4ff203a75d05df` (#36415) | Saved Mamba admission debit and nonvacuous marker writes retained |
| `12593d20ead3` | `8392c36bce22d3c54a6381aea6e003d6bf57719b` (#37165) | Deferred initialization cleared before speculative decode |

## Fusion implementation and guards

Compared historical extracted engine `5a50cb42c0c1a167241fea7da8ca9d8209e65cf7`
with the audited engine using Python ASTs (ignoring locations, not code):

- `models/nemotron_h.py`: `_latent_proj_fuses_shared_add` and
  `_apply_latent_projection` are exactly AST-identical.
- `layers/quantization/unquant.py`: `_can_accumulate_into_addend` and
  `apply_with_addend` are exactly AST-identical.
- `_bf16_gemm_dispatch_impl` is AST-identical after only the explicit renames
  `use_flashinfer_pr4266_bf16_gemm` -> `use_bf16_splitk_gemm` and
  `_flashinfer_pr4266_bf16_gemm` -> `_bf16_splitk_gemm`.

The model's forward calls the helper only for latent MoE, then performs the
existing TP reduction/shape restoration. Nonlatent shared output is added
separately; there is no duplicate shared add. Eligibility requires exactly
`ReplicatedLinear`, no bias, and `UnquantizedLinearMethod`: LoRA wrappers,
subclasses, quantized projections and biased projections retain normal forward.
No shared output also retains normal forward.

The accumulation guard requires CUDA, noncompiling, non-batch-invariant,
2D CUDA input, BF16 operands/addend, contiguous correctly shaped addend, no
bias and no gradients. Specialized splitK/Hopper/CuteDSL paths add to their
result; cuBLAS may accumulate into the supplied addend. These distinctions
remain unchanged. Existing five model regressions and CUDA addend/graph tests
remain in source; this audit does not claim they were executed as full imports
or that CUDA alias/capture/numerics were retested.

## Mamba indexing and admission call chains

`HybridLinearAttnBackend._init_track_ssm_indices` uses flattened cumulative
request starts for Mamba2. On-grid tracked positions index intermediate `h`;
off-grid positions carry sequence/end/recompute-destination metadata.
The non-Mamba2 path retains per-request chunk offsets. Newer KDA support adds
two returned fields, without replacing the Mamba2 split. Both metadata
conversion paths preserve the three recomputation fields; Mamba2 passes them
to the combined scan and sends returned track states to `_copy_ssm_states`.
The copy path retains recompute, intermediate and final-state destinations.

`ssd_combined._track_states_at` is exactly AST-identical to historical extracted
engine `b33a5227201dccdfa45a62275661375ba83a7c40`: flattened start/end pairs,
adjusted initial states, varlen state extraction, then alternating results.
The optional return requires varlen mode; recomputation runs only for nonempty
tracking metadata.

Admission now uses `req.kv.holds_mamba` rather than the old nullable field.
`add_one_req` captures `_mamba_gap_budget_for_req` before `init_load_back`;
the saved value passes through `_commit_prefill_admission` to
`_update_prefill_budget`. Both total/current budgets receive the debit and
the new-slot budget decrements once. Host-load delivery/reselection does not
recompute the reservation after binding ownership.

The cache test helpers `_fill_full_kv` and `_fill_mamba_state` are exactly
AST-identical to extracted engine `3c716ec8e08e86fe6752a10de346172937c54337`.
They assign into advanced indices instead of filling an advanced-index copy.
`ScheduleBatch.prepare_for_decode` clears all three deferred Mamba init fields
before the speculative-decode call and early return.

## Page-budget historical delta

Historical `1d8e0a494693` stopped the scheduler before a sub-page chunk.
Its helper/early-break are not byte-equivalent in the successor, and should
not be described as upstream-identical. The current ordinary
`_select_prefill_admission` floors the chunk by page size, rejects nonpositive
extent before host load, and the scheduler breaks on a non-CONTINUE result,
cleaning newly staged Mamba metadata/slots for rejected requests.
The common exact-chunk-fill path intentionally bills compute tokens separately
from page-ceiled KV allocation. Reintroducing an unconditional sub-page break
would incorrectly defeat that behavior. No additional model-specific copy is
needed. Existing guarded BREAKABLE/Marlin migration and its six prior source
tests remain separate evidence; CUDA qualification is still outstanding.

## Executed focused checks and limits

Local scratch receipt: `tmp/audit-nemotron-history-20260922.py` in the integration
workspace; bundled Python 3.12 with real torch 2.13 CPU dependencies.
The harness executes AST-extracted production methods, not a rewritten
implementation and not a full SGLang import:

- Four existing Mamba2 index tests passed (on-grid, off-grid, mixed, flat end
  coordinates), with zero skips.
- Actual admission/commit/update methods with mocked load-back: saved reserve
  produces total/current debits `(264, 256)` and remaining slots `1`.
  Negative control recomputing after ownership binds produces `(136, 128)`
  and remaining slots `2`, exposing the historical underdebit.
- Page size 64: ordinary remainder 63 rejects; 64 admits a 64-token chunk;
  intentional exact-fill remainder 63 admits 63 forward tokens.
- Actual decode-preparation method clears stale deferred metadata before its
  mocked speculative callee/early-return.
- Seven exact function AST comparisons plus the explicitly renamed dispatcher
  and four upstream ancestry checks passed.

No new implementation abstraction was introduced. The simplification decision
is to reuse covered common/upstream behavior, not duplicate old patches.
These checks close the named historical source-review items, not real CUDA
arithmetic, CUDA Graphs, serving pressure, latency or throughput acceptance.
