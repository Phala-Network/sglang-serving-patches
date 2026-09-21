# Kimi-K3 v0.5.20 source/profile candidate

This candidate exports ten source fixes. The first seven came from [Phala-Network/sglang PRs 34–40](https://github.com/Phala-Network/sglang/pulls); the HiCache reset, gauge refresh and async ACK changes are the final three commits on `codex/kimi-k3-v0520-async-ack-release-r1`. Source implementation and regression review belongs to the recorded source refs; this patch repository reviews applicability, deterministic export, dependencies and composition. A PR link or local branch name does not represent approval.

The [profile](../profiles/v0.5.20/kimi-k3.yaml) is the only patch selection source. The [catalog](../patches/sglang/v0.5.20/kimi-k3.manifest.json) records source commit/parent/tree, source ref, optional review PR, export argv/hash and conflicts. All ten fixes have common semantic scope, with validation restricted to Kimi-K3. Review-stack ancestry is not an implicit semantic dependency. Restorable-prefix requires file-storage-ownership, and the gauge-refresh patch requires the preceding reset-visibility patch whose temporary implementation it replaces. The chat-stream-close and request-owner variants conflict with the existing Qwen source PRs #3 and #7; selecting both requires source reconciliation.

## Reproduce provenance

Use Python 3.10+ and Git, with the source repository containing the recorded source commits and parents:

```sh
python -m unittest discover -s tests -v
python tools/validate_profile.py --source /path/to/sglang --receipt kimi-profile-receipt.json
```

The validator reads Git objects, compares every parent and source tree, re-exports exact bytes, verifies raw patch hashes and explicit dependencies/conflicts, and applies only the profile-selected deltas to the official base using a temporary Git index. It does not checkout source or reuse the review stack as its starting tree. The receipt contains raw profile/catalog hashes, per-patch source identities, byte counts/hashes and the actual final tree. JSON-compatible YAML needs only the standard library. Git attributes preserve raw profile/export bytes across Windows and Linux.

The local replay matches full tree `94aa4aeb1dc917d26f523517bdccaa346912bd16`, identical to development source `63d0313435d1a3da814664a1f10537f69fa8ec05` and composed source `22dfb99dfadbc06f5474ca594613986e9cff22b7`. The composed branch starts from clean regrouped commit `b873d248cdfb2ac62e9bbb1d14f45925c152f053`; the existing dirty checkout was not modified. Twelve validator fixture regressions cover corrupted exports/parents, dependency omission/order, unknown/conflicting selections, wrong final trees, raw line endings, and exclusion of unselected common patches and review ancestry.

The existing GitHub Actions workflow can fetch actual source refs/commits and run these tests plus export/apply/tree validation after the new source branch is published. Local results are not proof that a hosted CI run passed. This gate applies to the Kimi profile; no new verification claim is made for the existing Qwen profile. The repository had no workflows or CODEOWNERS at this base; no owner assignments are invented.

## Runtime evidence boundary

The async ACK stack changes the frozen full source tree. Existing standalone SGLang CPU/CUDA evidence remains historical evidence for the first seven-patch tree and cannot qualify the new three-patch delta. The source gate now requires `test/manual/test_hicache_async_ack_sync.py --gloo` to report exactly 15 tests with zero skips, failures or errors; that real-Gloo execution still requires the pinned official image or another environment with PyTorch Gloo. This metadata work runs no model/GPU workload. TP8, BF16 KV, FP32 KDA and context 1048576 are retained; observed DCP settings are 1 and 8, while L3 validation is limited to DCP1. Mooncake is not accepted for Kimi-K3. Governor is disabled, and an enabled Governor combination has not been tested. Source approval, image publication and deployment are separate stages and are not claimed here.

The [historical validation reuse record](validation/kimi-historical/validation-reuse.json) binds the original [CPU receipt](validation/kimi-historical/historical-r12-final-cpu.json) and [CUDA receipt](validation/kimi-historical/historical-r12-final-cuda.json) by SHA-256. The nine CPU suites total 192 test methods; CUDA records 58 cases, of which 36 passed and 22 skipped. These are original execution counts for tree `25a790a2fb58644a31c15ce1bcaf3b4d37733574`, not new runs, a qualification of `94aa4aeb1dc917d26f523517bdccaa346912bd16`, or a deduplicated CPU/CUDA coverage count. Dependency versions are recorded, but the Mooncake wheel build commit remains unknown; a reference-source commit is not its build provenance. No dependency implementation is added by this migration.

Hosted [Actions run 35490913861](https://github.com/Phala-Network/sglang-serving-patches/actions/runs/35490913861) passed the prior seven-patch export/apply/tree gate and 12 validator regressions on metadata commit `2954c11976ff0b051794772020792b4bc26c6d08`. It does not cover the new 0008–0010 exports or final tree. Their hosted run status must be established separately after publication.
