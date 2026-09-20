# GLM profile verification

The JSON-compatible YAML profiles are the sole ordered patch selection. Edit
implementation in the linked SGLang source PR, then export its exact parent diff:

```sh
git diff --binary --full-index SOURCE_PARENT SOURCE_COMMIT > selected.patch
```

Use a byte-preserving redirect (or Python subprocess bytes on Windows), and record
the complete commit, parent, SHA-256, source PR, category and explicit dependencies.
Do not edit exported implementation by hand. An external dependency overlay also
records its repository/path and commit, or exact version and original file SHA-256.

From this repository root, with the source commits available in a local fork:

```sh
python scripts/verify_glm_profiles.py --self-test
python scripts/verify_glm_profiles.py --source-repo ../sglang \
  --profile profiles/v0.5.20/glm-5.3-mooncake.yaml \
  --profile profiles/v0.5.20/glm-5.3-host-async-ack.yaml \
  --output verification/glm-profiles.json
```

Verification requires every source commit's exact single parent; re-exports and
compares patch bytes; checks ordered dependencies; applies every selected patch
with `git apply --index` from the pinned official commit; compares the complete
resulting Git tree and, when supplied, deployed `python/sglang` subtree identity.
The optional `engine_commit` must identify the same complete tree. A separate
temporary Git repository, index and checkout preserve the source worktree.

Every profile declares its affected regression scripts. They run against the
materialized selection with its `python` directory on `PYTHONPATH`, explicitly
bound source paths, and without Governor. The FlashInfer test may override only
`FLASHINFER_ALLREDUCE_SOURCE`, pointing to a file within the materialized tree.
The self-test exercises a real Git export/apply and rejects changed hashes,
missing dependencies, incorrect parents/trees, and modified patch bytes even
when the recorded patch hash is updated.

The GLM workflow fetches pinned public fork commits and runs these same checks
for the two v0.5.20 profiles. Source PR URLs identify provenance; neither their
presence nor this CI proves review approval. The result is source/export/tree
and CPU regression evidence. It does not establish GPU, distributed Gloo,
image, deployment, or production acceptance. Governor-enabled combinations
need a separate verifier and their own integration evidence.
