# Kimi-K3 v0.5.20 source/profile candidate

This candidate exports seven source fixes from [Phala-Network/sglang PRs 34–40](https://github.com/Phala-Network/sglang/pulls). Source implementation and regression review belongs to those PRs; this PR reviews applicability, deterministic export, dependencies and composition. None of these PR links represents approval.

The [profile](../profiles/v0.5.20/kimi-k3.yaml) is the only patch selection source. The [catalog](../patches/sglang/v0.5.20/kimi-k3.manifest.json) records source commit/parent/tree, review PR, export argv/hash and conflicts. All seven fixes have common semantic scope, with validation restricted to Kimi-K3. Review-stack ancestry is not an implicit semantic dependency. Only restorable-prefix requires file-storage-ownership. The chat-stream-close and request-owner variants conflict with the existing Qwen source PRs #3 and #7; selecting both requires source reconciliation.

## Reproduce provenance

Use Python 3.10+ and Git, with the source repository containing the recorded source commits and parents:

```sh
python -m unittest discover -s tests -v
python tools/validate_profile.py --source /path/to/sglang --receipt kimi-profile-receipt.json
```

The validator reads Git objects, compares every parent and source tree, re-exports exact bytes, verifies raw patch hashes and explicit dependencies/conflicts, and applies only the profile-selected deltas to the official base using a temporary Git index. It does not checkout source or reuse the review stack as its starting tree. The receipt contains raw profile/catalog hashes, per-patch source identities, byte counts/hashes and the actual final tree. JSON-compatible YAML needs only the standard library. Git attributes preserve raw profile/export bytes across Windows and Linux.

The local replay matches full tree `25a790a2fb58644a31c15ce1bcaf3b4d37733574`, identical to frozen tested source `739b517714012a8766a7d09d473f82aabd7f4d28` and regrouped source `b873d248cdfb2ac62e9bbb1d14f45925c152f053`. Twelve fixture regressions cover corrupted exports/parents, dependency omission/order, unknown/conflicting selections, wrong final trees, raw line endings, and exclusion of unselected common patches and review ancestry.

The new GitHub Actions workflow fetches actual source refs/commits and runs these tests plus export/apply/tree validation. Local results are not proof that a hosted CI run passed. This gate applies to the Kimi profile; no new verification claim is made for the existing Qwen profile. The repository had no workflows or CODEOWNERS at this base; no owner assignments are invented.

## Runtime evidence boundary

Source regrouping does not change the frozen full source tree. Existing standalone SGLang CPU/CUDA evidence can be reused only with that binding and its original execution scope. This metadata work runs no model/GPU workload. TP8, BF16 KV, FP32 KDA and context 1048576 are retained; observed DCP settings are 1 and 8, while L3 validation is limited to DCP1. Mooncake is not accepted for Kimi-K3. Governor is disabled, and an enabled Governor combination has not been tested. Source approval, image publication and deployment are separate stages and are not claimed here.
