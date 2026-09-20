# v0.5.19 historical runtime profiles

These explicit profiles reconstruct the engine source carried by six currently deployed models. They are **migration candidates**, not minimal new model profiles. For example, Qwen2.5 and Gemma consume the same historical Qwen/Gemma image; its Qwen GGUF code is present but is not thereby required or exercised by those models. Muse and Nemotron similarly share an inherited image lineage. All inherited selections are visible; none is pulled in by an implicit common directory rule.

The normalized source retains the full official upstream tree and applies only historical changes under python/, test/, sgl-kernel/ and 3rdparty/. Packaging/templates/external dependency patches are preserved separately in phala-models-compose historical inputs. The final tree is a complete Git tree, **not** a file-list hash and **not** the original tree containing old release recipes. No runtime source behavior was changed during extraction.

| Model | Explicit patches | Source head | Complete engine tree |
|---|---:|---|---|
| gemma-4-26b-a4b-uncensored | 9 | `d0b3e70cbc5ed3cc757d22e79ffa1fff28f58571` | `5da72f4fcacb3889d4bfa9a2e35a1debac903aa4` |
| muse-glimmer-30b | 23 | `a54a1d5bb9f4ee2034c281f99bab4391eb70c77c` | `2e5ff571325982ad59c5840e5d838c442784b0f1` |
| nemotron-3.5-lightning | 29 | `9cfc79c4b497bc883132f5e2bcd5d012790f3d12` | `13b00c9d8ca5916d6506926783fcc743dbf43ee9` |
| qwen-2.5-7b | 9 | `d0b3e70cbc5ed3cc757d22e79ffa1fff28f58571` | `5da72f4fcacb3889d4bfa9a2e35a1debac903aa4` |
| qwen3.6-27b | 26 | `711978779936d1918d038de8515e33f968cb5193` | `d209baf0019b73d3126b85401154de8d0fa124fd` |
| qwen3.8-27b-uncensored | 9 | `d0b3e70cbc5ed3cc757d22e79ffa1fff28f58571` | `5da72f4fcacb3889d4bfa9a2e35a1debac903aa4` |

Shared implementations are stored once and selected by path/hash. Sequential parent dependencies conservatively preserve the tested historical order; they are not assertions that every earlier feature is logically required. Distinct Qwen/Muse/Nemotron cancellation versions have different surrounding implementations and regression sets; do not collapse them solely because they reference upstream #35255. The existing v0.5.20 work is a separate baseline and is not silently reused here.

Run `python tools/verify_v0519_profiles.py --source-repo /path/to/sglang`. It checks source parent, re-exported bytes, hash, ordered dependency selection, actual application and complete tree at **every step**. `tests/test_profile_verifier.py` exercises corruption, rehashed tampering, wrong parent, missing dependencies, duplicate patches and wrong final tree. CI performs the same source/application verification. This is separate from historical GPU/protocol evidence and approval.

No Governor is installed or selected. PIG v0.12.29 and TAIL remain independently owned components. No new image, tag, main rewrite, deployment, route mutation or benchmark is part of this migration.

Issue-by-issue source reviews are indexed in `SOURCE_REVIEWS.md`. The five full-lineage PRs are generated comparison views only; changes are maintained in individual issue PRs. Original historical source parents are fetched and checked by CI, not accepted from metadata alone.
