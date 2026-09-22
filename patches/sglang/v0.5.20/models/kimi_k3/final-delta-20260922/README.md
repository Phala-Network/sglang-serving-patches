# Kimi K3 final runtime delta (2026-09-22)

This directory contains only the three commits added after the existing Kimi K3
v0.5.20 ten-patch stack. It does not replace or modify
`profiles/v0.5.20/kimi-k3.yaml`, the shared manifest, global patch ordering, or
the validator.

## Required baseline

- Patch repository baseline: `7f353ede6782e45d26df4daf75abdf38d260015a`
- Existing Kimi profile composed engine commit:
  `22dfb99dfadbc06f5474ca594613986e9cff22b7`
- Existing Kimi profile composed engine tree:
  `94aa4aeb1dc917d26f523517bdccaa346912bd16`

Apply these files in lexical order after that existing stack:

1. `0001-fix-hicache-account-for-1GB-HugeTLB-host-pools.patch`
2. `0002-Fix-staggered-HugeTLB-budgets-and-await-health-probe.patch`
3. `0003-Add-focused-B300-registered-KV-transfer-extension-an.patch`

The patches correspond to engine commits `d70f095`, `9219229`, and `a479d6c`.
They were exported with full Git indexes and binary support. Applying them with
`git am` to `22dfb99` produced tree
`c900062f246b56bf01e71b80533888d6222d2906`, exactly matching the reviewed
final runtime source at `a479d6ce0f7fdbefcafc4fac93af3737fc5df7f7`.

See `apply-receipt.json` for full identities, patch hashes, and the reproduced
commit sequence.
