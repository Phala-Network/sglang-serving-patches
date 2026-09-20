# v0.5.19 issue-level source review index

Every exported record has its own exact-parent source PR. Follow-up regression-only commits remain separately visible and explicitly depend on their actual parent. These are draft reviews, not approvals. Full lineage PRs #29-33 are generated comparison views, not a second manual maintenance entrypoint. Fix issue branches, regenerate exports and propagate reviewed dependencies; never hand-edit exported implementations or generated aggregate views.

The four original deployed histories are available under `codex/archive-five-cvm-v0519-{qwen38-gemma4,qwen36,muse,nemotron}`. Archive branches are immutable provenance references, not maintenance branches. The verifier fetches original and extracted heads and proves exact historical source/test projection before export/application checks.

| Historical commit | Directory ownership | Issue / regression | Source review | Extracted commit |
|---|---|---|---|---|
| `5404f7600755` | models/qwen-gguf | Fix Qwen3.5 GGUF loading on official SGLang v0.5.19 | [PR](https://github.com/Phala-Network/sglang/pull/54) | `81881bd7c1a0d867513dbef9b650656fdc1fa9e2` |
| `d67e821bd5ea` | models/qwen-gguf | Audit GGUF load completeness by shared parameter identity | [PR](https://github.com/Phala-Network/sglang/pull/55) | `39eedc17eb620a3533ff4633141d73a0d5a89016` |
| `ea31b4a3509f` | models/qwen-gguf | Preserve Qwen tool argument schemas and complete streaming calls | [PR](https://github.com/Phala-Network/sglang/pull/56) | `55c45e7499621201fbabe73e10ffdea401e0aa5e` |
| `79e215cde60b` | common | Supply llguidance mask callbacks to the reasoning wrapper | [PR](https://github.com/Phala-Network/sglang/pull/57) | `97882c58422b6253ae994aa39f9d34825b038654` |
| `e26b9f4dae32` | common | Preserve local schema reference roots for named tool choice | [PR](https://github.com/Phala-Network/sglang/pull/58) | `6ecc100728f6b85500800bb683fd2f9743340569` |
| `f80677f937c5` | common | Honor checkpoint mode-specific sampling defaults and explicit overrides | [PR](https://github.com/Phala-Network/sglang/pull/59) | `5a9b0690dddaf0100acabc1ed0eadccb0e0d1255` |
| `2b2584575aa5` | models/qwen-gguf | Add audited Qwen3.5 GGUF vision projector loading | [PR](https://github.com/Phala-Network/sglang/pull/60) | `788a8983750cd29aaee5f07ce5f937e7ae1e623f` |
| `c4afa9828243` | models/qwen-gguf | Use tensor-core BF16 GEMM for large Q8_0 prefills | [PR](https://github.com/Phala-Network/sglang/pull/61) | `be0e34807dfb65dda85877bb7ca9ec17b7a05430` |
| `82da9278e229` | common | Backport upstream 35255 dispatched request cancellation repair | [PR](https://github.com/Phala-Network/sglang/pull/62) | `d0b3e70cbc5ed3cc757d22e79ffa1fff28f58571` |
| `cc713697cb1b` | models/qwen3-family | fix(openai): harden Qwen3 tool calls and structured output | [PR](https://github.com/Phala-Network/sglang/pull/63) | `28238ec4007a4aab04e61295031fdc4f00d3f47a` |
| `ac6e301b2c45` | models/qwen3-family | fix(openai): normalize Qwen3.5 system messages | [PR](https://github.com/Phala-Network/sglang/pull/64) | `354b7c6c3f0acb2d2b0d54fdb09c4f908a7f4325` |
| `da8da902526c` | models/qwen3-family | fix(openai): preserve Qwen3.5 reasoning tool history | [PR](https://github.com/Phala-Network/sglang/pull/65) | `c30384652e5478f49c2a542af10c46989275fb8b` |
| `7dd1e4933610` | models/qwen3-family | fix(openai): differentiate Qwen3.5 reasoning effort tiers | [PR](https://github.com/Phala-Network/sglang/pull/66) | `ea92ab4c5f7be0b8771b14bce9648951ec3a9832` |
| `7e4e69f5850f` | models/qwen3-family | fix(openai): enforce Qwen reasoning effort ranges | [PR](https://github.com/Phala-Network/sglang/pull/67) | `538e30d61375ddeacbf6f6eeefe4606bc14e3e02` |
| `6d6103699ea4` | common | fix(openai): honor disabled nested reasoning | [PR](https://github.com/Phala-Network/sglang/pull/68) | `cd31831d54f55659b2c241d72ff098197f93d1a4` |
| `96cd94344d57` | models/qwen3-family | perf(openai): skip unbounded Qwen strict grammar | [PR](https://github.com/Phala-Network/sglang/pull/69) | `b85619fd04c3948469edb47aed99f400f49eae2b` |
| `d61efbc4c4f5` | common | fix(openai): drop orphan streaming tool deltas | [PR](https://github.com/Phala-Network/sglang/pull/70) | `9b1b0671abe6d94ca05c2fdd341846f91fee23a0` |
| `47d684c188fd` | models/qwen3-family | fix(openai): finalize Qwen tool result turns | [PR](https://github.com/Phala-Network/sglang/pull/71) | `b2d182e4d645bd1103f0734eeee3be5e39862bef` |
| `27487759d660` | models/qwen3-family | fix(openai): bound default Qwen reasoning | [PR](https://github.com/Phala-Network/sglang/pull/72) | `7a6812c460d5941e3af0f2db3fd8771edf7ed438` |
| `c0b47b4d9a80` | models/qwen3-family | fix(openai): restore Qwen reasoning quality budget | [PR](https://github.com/Phala-Network/sglang/pull/73) | `7846a276b049d34a96a51d4497d168a036ea1f40` |
| `b69731aa5a70` | common | fix(openai): preserve reasoning visibility contract | [PR](https://github.com/Phala-Network/sglang/pull/74) | `5e3f909d22f2e79ba7c7b85fa747f762109aab99` |
| `a17450df7fe0` | common | Fix: abort handling for dispatched requests after client disconnect (#35255) | [PR](https://github.com/Phala-Network/sglang/pull/75) | `96e883d1e796b0ad0e86af386eb113708760806a` |
| `0b21f9af0f2f` | models/qwen3-family | [Performance] Optimize Qwen3.5 GDN prefill projection layouts (#36267) | [PR](https://github.com/Phala-Network/sglang/pull/76) | `ae13fff53317c8db42f2bda64b20a2fe280591e2` |
| `223e067187a6` | common | test(qwen38): adapt Phala fixtures to runtime config bags | [PR](https://github.com/Phala-Network/sglang/pull/77) | `4c25322c802951ad5fb6dc85906998f1a01efac2` |
| `29f0b04675b4` | models/qwen3-family | test(openai): complete Qwen reasoning fixture | [PR](https://github.com/Phala-Network/sglang/pull/78) | `82c5597d4182d86cac839c7869d52e8c8a381c9b` |
| `4dcc87bb9a11` | common | fix(runtime): harden media watchdog and disconnect abort | [PR](https://github.com/Phala-Network/sglang/pull/79) | `42cac46e56d82d587d9170614cae4c22a4cef164` |
| `119767a19ad0` | common | fix(runtime): reject oversized media requests before decode | [PR](https://github.com/Phala-Network/sglang/pull/80) | `6c6cdbc75c7de2704141e6f2ab02cc9417fb02f0` |
| `58c4ebfd0be5` | common | test(multimodal): exercise eager PIL system-error path | [PR](https://github.com/Phala-Network/sglang/pull/81) | `a1c281180bbcfee4e90081bc23aeb05c88e00314` |
| `66599f0839c0` | common | test(qwen38): adapt pre-MM fixture to v0.5.19 config bag | [PR](https://github.com/Phala-Network/sglang/pull/82) | `cdea3b3c96d410e1e21e1013eed39a6388fc4f2e` |
| `3852646c7dfd` | models/qwen3-family | fix(qwen3.5): map extended reasoning effort aliases | [PR](https://github.com/Phala-Network/sglang/pull/83) | `cd196db84369a0de957bde93c31a44ee67adbc55` |
| `70bcd26c4621` | models/qwen3-family | fix(qwen3.5): give explicit medium effort a bounded 4096-token budget | [PR](https://github.com/Phala-Network/sglang/pull/84) | `d70dbf79e7fee22a1db15dbc5df25a1d7398a5d7` |
| `17cb69777837` | common | fix(openai): normalize null tool schema fields | [PR](https://github.com/Phala-Network/sglang/pull/85) | `bdec50dcf6f5aaf802f9962ecd0092fdd7eebdc6` |
| `2a6898f3c996` | models/qwen3-family | fix(qwen): close empty XML calls and preserve required schema semantics | [PR](https://github.com/Phala-Network/sglang/pull/86) | `774c19539bd532090df7b12994b0c01a9b4fbf7a` |
| `fdcb90492c7c` | models/qwen3-family | build: add CPU-only native wheel qualification target | [PR](https://github.com/Phala-Network/sglang/pull/87) | `772a63931ff9719eb5e9fd123f95984ab3c20de0` |
| `15966fe477b8` | models/qwen3-family | test(qwen): exercise normalized request schemas and typed map controls | [PR](https://github.com/Phala-Network/sglang/pull/88) | `711978779936d1918d038de8515e33f968cb5193` |
| `65a1b3f10fd0` | models/nemotron | Fuse Nemotron latent MoE projection and shared add (#30430) | [PR](https://github.com/Phala-Network/sglang/pull/89) | `5a50cb42c0c1a167241fea7da8ca9d8209e65cf7` |
| `b07c939d0f55` | common | perf: use Gumbel-max trick in the main sampler to cut decode CPU dispatch (#38117) | [PR](https://github.com/Phala-Network/sglang/pull/90) | `002883d4473bd4e0ffcfa557ac7e6c8723a7daf4` |
| `61ab8c2adb9c` | common | fix(llguidance): pin host vocab masks before async H2D copy | [PR](https://github.com/Phala-Network/sglang/pull/91) | `b431a69ddfaf3b2f953b75215f0c6d1095fdb733` |
| `405fa1086fdb` | models/muse-glimmer | fix(muse): parse required tool calls natively | [PR](https://github.com/Phala-Network/sglang/pull/92) | `287188b4806f33ff7e4702668a6836b5c5b2987d` |
| `c5af5ab92184` | models/muse-glimmer | fix(muse-glimmer): backport channel-framed guided decoding boundary | [PR](https://github.com/Phala-Network/sglang/pull/93) | `f6adaf751a72201a0280ae7ba6446791924e98e6` |
| `7984762a1925` | common | fix(openai): expose reasoning usage in standard details | [PR](https://github.com/Phala-Network/sglang/pull/94) | `353a12fabcd98597a83f81885be52cba8c8e82f2` |
| `889dac086485` | models/muse-glimmer | fix(muse): honor OpenRouter tool and history contracts | [PR](https://github.com/Phala-Network/sglang/pull/95) | `235ce2bcc40a5b4fc5e5e89758f8d5c0b3280fc7` |
| `7aad27962602` | models/muse-glimmer | fix(muse): default structured output to direct final | [PR](https://github.com/Phala-Network/sglang/pull/96) | `2ef83173697fb4993f636cffb63439ffef6f99c1` |
| `c5052c199e05` | models/muse-glimmer | fix(muse): preserve named choice and v0.5.18 regressions | [PR](https://github.com/Phala-Network/sglang/pull/97) | `b22934ade600777fe7b5cdf0f8a54ce6d4096651` |
| `7070885b6c51` | models/muse-glimmer | fix(muse): enforce required tool choice | [PR](https://github.com/Phala-Network/sglang/pull/98) | `6d7a2dc746935afa3ccbcd5f0e9bb727f52bf84d` |
| `2224d5c89971` | models/muse-glimmer | fix(muse-glimmer): harden tool calls and structured output | [PR](https://github.com/Phala-Network/sglang/pull/99) | `c2d241b80ef0e4e0e3aaf517567287368ac56fe3` |
| `752cbf71d2fc` | common | Fix mamba radix cache ssm state indexing (#37836) | [PR](https://github.com/Phala-Network/sglang/pull/100) | `b33a5227201dccdfa45a62275661375ba83a7c40` |
| `72d09f13ce3e` | common | [Fix] Vacuous marker writes in the cache tests, and an undebited Mamba admission slot (#36415) | [PR](https://github.com/Phala-Network/sglang/pull/101) | `3c716ec8e08e86fe6752a10de346172937c54337` |
| `12593d20ead3` | common | [Bugfix][Mamba] Clear deferred init metadata before speculative decode (#37165) | [PR](https://github.com/Phala-Network/sglang/pull/102) | `0775c972ac7eb227e9fd852e79bfb78049439403` |
| `66c99cdb3906` | common | fix: add opt-in bounded XGrammar JSON whitespace | [PR](https://github.com/Phala-Network/sglang/pull/103) | `4aca87a34545a2aa6b92f1887893feb069c43e4e` |
| `87d669f137cb` | common | fix: qualify pinned XGrammar 0.2.6 schema regressions | [PR](https://github.com/Phala-Network/sglang/pull/104) | `d2334dc9c0ab93c6bc2b629ae12d4e26d4855b3f` |
| `93a9c811a9af` | models/nemotron | Fix Nemotron native tool boundaries and exact small-object JSON order | [PR](https://github.com/Phala-Network/sglang/pull/105) | `010d115a7fa3bd926b6e693ae347fa8b43f2aa9f` |
| `6928845df367` | common | Bound emitted reasoning usage and preserve exact XGrammar patch bytes | [PR](https://github.com/Phala-Network/sglang/pull/106) | `88c70bc7f39f4037ff22bd4bc3e2918ac3058f04` |
| `ed810727c954` | models/nemotron | fix: keep truncated Nemotron thoughts out of tool execution | [PR](https://github.com/Phala-Network/sglang/pull/107) | `c8c1cfccdb7ee6bd251949b639880cc876fbabd0` |
| `01433fd33149` | models/nemotron | fix: withhold unfinished Nemotron tool calls at stream boundaries | [PR](https://github.com/Phala-Network/sglang/pull/108) | `c977122cefeef784c33f0e11c2b841c8111e76cb` |
| `69743bca633b` | models/muse-glimmer | fix: align Muse template instructions with constrained JSON formats | [PR](https://github.com/Phala-Network/sglang/pull/109) | `6445186b9110860eca2836fc425d11e0e3ae9b32` |
| `ed4266b4513f` | models/muse-glimmer | fix: pass Muse tool constraints through the actual template call boundary | [PR](https://github.com/Phala-Network/sglang/pull/110) | `29aca0c55e2c7606260333bea0d667eea9695940` |
| `eec6b2e25ee0` | common | fix: preserve scheduler ownership when Muse requests are cancelled | [PR](https://github.com/Phala-Network/sglang/pull/111) | `a54a1d5bb9f4ee2034c281f99bab4391eb70c77c` |
| `5f9f960c28a1` | models/nemotron | Fix Nemotron structured output contracts and request lifecycle | [PR](https://github.com/Phala-Network/sglang/pull/112) | `3c06073c3d0b3ada4ed413d25d543350386c3f72` |
| `4dbfdf98a4d5` | models/nemotron | fix(nemotron): distinguish literal data from reasoning control tokens | [PR](https://github.com/Phala-Network/sglang/pull/113) | `09361b0f5e5bc3d274f560f4f830e1205a200241` |
| `ec6f1c44c8a7` | common | fix(serving): abort dispatched requests on streaming cancellation | [PR](https://github.com/Phala-Network/sglang/pull/114) | `ac0834cff92db9cb4667e3d674bbd26ce28735a5` |
| `068de9fd66d1` | common | test: model dispatch ownership in parallel sampling cleanup fixtures | [PR](https://github.com/Phala-Network/sglang/pull/115) | `c25af5ffb848ac4f4754117c039f9c5b0ea60c0e` |
| `6d3d45b55d98` | common | Fix stable Marlin routing and honor FP32 NVFP4 reduction | [PR](https://github.com/Phala-Network/sglang/pull/116) | `e27330c9722dcc837ea2452b5256d7a63f325b82` |
| `f97b21d20d93` | models/nemotron | fix: bound XGrammar repetition state and compile JSON string FSM blocks | [PR](https://github.com/Phala-Network/sglang/pull/117) | `ee2f690dd80ab7deb722d1613b2c5cffbf78fea2` |
| `f65bb7af2030` | models/nemotron | fix: preserve const-constrained XML tool argument types | [PR](https://github.com/Phala-Network/sglang/pull/118) | `76d1c6ab2ebcb2d87b19e17c14b97dd2e9681a21` |
| `1d8e0a494693` | common | fix: align chunk budget to KV pages | [PR](https://github.com/Phala-Network/sglang/pull/119) | `d668757274a2fee4f6e0f464b66066bdd7e28bc7` |
| `cfe6dbb89416` | common | fix: enable breakable prefill graphs for hybrid layers | [PR](https://github.com/Phala-Network/sglang/pull/120) | `9cfc79c4b497bc883132f5e2bcd5d012790f3d12` |
