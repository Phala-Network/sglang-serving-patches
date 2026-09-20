# Contributing

Make engine changes and focused regressions in the complete source tree at
[Phala-Network/sglang](https://github.com/Phala-Network/sglang). Keep common fixes
shared and preserve model, hardware and topology conditions where needed.

Do not maintain hand-edited duplicate patches, per-model manifests/profiles,
long-lived per-model export branches or independent model CI here. Keep the
actual generated patch collection current with the frozen complete engine source.

For each maintained source update:

1. Pin the official upstream commit and complete Phala engine commit/tree.
2. Update the frozen identities in `scripts/export.py`, then regenerate the
   collection, manifest and series. Preserve source attribution and licenses.
3. Verify applying the export to the pinned upstream reproduces the expected
   complete tree. Reuse applicable source validation and identify its scope;
   export equivalence alone does not prove runtime or cross-model acceptance.
4. Publish the actual patches with their provenance and validation boundaries.
   Regenerate after source changes instead of editing both copies. Keep one
   common copy, explicit model/dependency ownership, and explicit external
   Governor hook ownership. Do not silently incorporate controller code.

Before retiring historical branches, preserve exact heads under archive tags
and verify remote tags resolve to those commits. Retain PRs, failed results and
unique evidence. Review archived fixes against current source before reuse.

Documentation changes need diff, link and repository-state checks, not a new
GPU benchmark or a separate CI framework.
