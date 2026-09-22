# Separate frozen PIG candidate receipt

This is provenance for the independently built PIG candidate, not the active
unified model successor. It does not replace this branch's series, selectors,
manifest, engine identity or Governor compatibility claims.

| Immutable input or output | Identity |
| --- | --- |
| Complete engine | `e02dfa1256c5d7d6e8b731d439229d5aca72cbe5` |
| Engine tree | `ae0e7307e3dcf2314b7eb51e26a17207073e0f0a` |
| Governor 0.2.4 source / ABI | `c27f4d10905eb7b2ef1bb2b01c14e8cc09236b44` / ABI4 plus replacement symbol |
| Governor tree | `710e94ff38b385ca9bb6d9737a6515fa4910f9d9` |
| Frozen serving-patches export | `fb38d016e1708dbf145f1f4e8f310c4ce5144e36` |
| Export tree | `a6dff0ca61e9fd3ef84290b297f34854f553ea63` |
| Image config ID | `sha256:eda5fcd7fad9862fd6247a29d2c8ba96cc00f595a55b4c4dfbfc6ed2684358e8` |
| Private transport manifest | `sha256:5bc0e48d27f7aae5618471661e6643b484cd1ec29623fcbddc261445bb0a8c9b` |
| Native library SHA256 | `c0c2fc8ee9908f5699e0bf2d44061b288455a445f8284a59ba3ae449239c415a` |
| Ordered 82 diff-ID list, compact JSON SHA256 | `515b8ebc8f249ec1b2b3aeb57f1009439420f2ac0a5380e3fd53b47b309850c1` |

The owner performed one actual build on September 22, 2026,
14:40:55–14:46:59 UTC. The private compression-preserving export reused all four
RUN steps and retained the exact config and ordered RootFS diff IDs.
The config identity and transport manifest digest are different objects, not
interchangeable labels.

Final-image CPU receipt passed direct HF/SGLang CLI checks, installed source
hashes, package 0.2.4/component contract, ABI4 and
`pig_governor_observe_replacement`, 164 Python tests including synthetic auth,
and four real-core CPU regressions. Tests mounted test/metadata/helper inputs,
not runtime implementation, library or virtualenv overlays. The independent
32-step export check verified every intermediate tree.

Read-back on September 22 confirms the existing
`codex/pig-v4-capacity-compat-export-20260922` branch and immutable GitHub commit
at `fb38d016...`, tree `a6dff0ca...`. It descends from `814f88dc...` through
`bd25c150...`; no active union metadata was replaced to preserve that source.
This receipt does not create a new PR, select a new engine or rebuild/relabel
the qualified image.

GPU805 transfer/identity check and authorized GPU acceptance remain separate
owner work at receipt time. CPU tests are not live service TOKEN verification,
GPU acceptance, or authorization to publish official SGLang image tags.
No public image digest or production acceptance is claimed here.

Owner evidence: `tmp/pig-next-candidate-024-20260922/PRIVATE-HANDOFF.md`,
`builder-evidence/qualification/qualified.json`,
`builder-evidence/private-transport-receipt.json` and `build-execution.json`
in the integration workspace. Mutable transport endpoints are deliberately
omitted from this durable provenance record.
