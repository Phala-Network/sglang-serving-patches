# 全现役模型历史修复维护覆盖表

审计日期：2026-09-21。本文是实际维护盘点，不是“所有模型已整合/接受”的声明。

唯一冻结比较对象为 `4281309187007db579a2195f40adfd4baa538528`，tree `83dcb00885129cc2afefdce2e169ebba697a9a67`，官方基线 `94602c9c2b7cbdb8efd5c52802dac6a1c180089e`（v0.5.20）。此源未被本审计修改。后继源的补丁整合与当前镜像构建是不同阶段；不得把后继候选的新增修复归到 428 或悄悄替换已冻结构建输入。

## 逐模型维护状态

| 模型 | 历史源（完整 SHA 见 JSON） | 当前 428 的位置/覆盖 | 证据与接受边界 |
|---|---|---|---|
| Qwen3.8-27B-Uncensored | [82da9278e229](https://github.com/Phala-Network/sglang/commit/82da9278e229402abcb50b46ee5a57e801bb651c) | 现有 Qwen/common 有 parser/schema/cancel 重叠；GGUF vision 与 checkpoint sampling helper 等历史模块未迁移。 | 不得将普通 Qwen/Governor 源码测试当作 GGUF/Q8_0/vision 接受。 |
| Gemma-4-26B-A4B-Uncensored | [82da9278e229](https://github.com/Phala-Network/sglang/commit/82da9278e229402abcb50b46ee5a57e801bb651c) | 继承同一历史镜像公共修复；无独立 Gemma 专属增量由本 handoff 证明。 | 共享镜像不等于执行 Qwen GGUF 路径；须保留 Gemma 实际模型/模板边界。 |
| Qwen2.5-7B-Instruct | [82da9278e229](https://github.com/Phala-Network/sglang/commit/82da9278e229402abcb50b46ee5a57e801bb651c) | 同一历史镜像公共修复需逐项判适用；不能按模型名复制 Qwen3.5/GGUF 增量。 | 历史只有功能接受，未宣称吞吐资格。 |
| Qwen3.6-27B | [1a56fbb0dc48](https://github.com/Phala-Network/sglang/commit/1a56fbb0dc48ec3fb2b4b629fc4e74a3b57c639a) | 模板/effort/history/schema/media/watchdog 大量存在 common 对应实现；旧行为完整等价仍待回归，尤其 native XGrammar XML/required 语义。 | 历史 XGrammar 0.2.1 修复不能与 0.2.6 包盲叠。 |
| Muse-Glimmer-30B | [eec6b2e25ee0](https://github.com/Phala-Network/sglang/commit/eec6b2e25ee098d04475e4784caad7b18021393b) | 仅 Gumbel sampler 与 deferred-Mamba 两条可证明上游全量吸收；Muse parser/channel/template/cardinality 历史增量未整体迁移。 | llguidance callbacks/pinning 与 typed reasoning usage 为确认 common 缺口；取消历史实现需和 current common 合并。 |
| Nemotron-3.5-Lightning | [cfe6dbb89416](https://github.com/Phala-Network/sglang/commit/cfe6dbb89416065555d4a2f0d2260704680136ec) | 共享 Muse ancestry 不代表需开启 Muse 行为；literal/control reasoning、complete tool、Marlin/FP32、BREAKABLE graph 等需模型语义迁移。 | 保留 262144/BF16/Mamba/EAGLE 前提；历史 Goodput 0.71498<0.7338 是用户 override，不能改写 PASS。 |
| GLM-5.3 | [d3c8af2c2800](https://github.com/Phala-Network/sglang/commit/d3c8af2c2800970b17b97a03d0ec9d051ccedd53) | 九个逻辑增量已经进入 428；ACK 两个原提交合并一个逻辑项，另有格式修正。 | 66 CPU unittest+22 SSD 含两进程 Gloo；不是新组合 GPU/Governor-on-GLM 接受。 |
| Kimi-K3 | [b873d248cdfb](https://github.com/Phala-Network/sglang/commit/b873d248cdfb2ac62e9bbb1d14f45925c152f053) | chat-close 由 common 覆盖；delayed request-owner、absolute checkpoint、prefill seq cap、file quota/prefix 与 completed-chunk guards 未全部在 428。 | 原 192 CPU /36 CUDA pass+22 skip 限原源/依赖；DCP8 logical512/physical64 不由 GLM page64 测试证明；next-source 尚未验证。 |
| DeepSeek-V4.1-Flash | [b6a5ec4af0f7](https://github.com/Phala-Network/sglang/commit/b6a5ec4af0f7981cab954de9a5f4e9ad16fd6948) | 26 导出未整体进入 428；native support/ABI/bitmap 必须成闭合链迁移，不能只摘 bitmap。 | 运行源 9acba212 与 classified b6a5 tree相同；候选协议仍失败；全局 437b protocol monkeypatch 必须模型 guard。 |
| Qwen3.8-27B（当前 common/Governor 源码目标） | [428130918700](https://github.com/Phala-Network/sglang/commit/4281309187007db579a2195f40adfd4baa538528) | 这是本冻结源已测试的 common/GLM/Governor 组合入口，不是上面九种历史维护覆盖都完成的声明。 | Governor ABI v1 仅 TP1/PP1/DP1、non-overlap、无 disaggregation 的既有 capability 范围。 |

## 分类方法和不能越过的边界

- **上游已覆盖**：原始完整补丁可对独立 index 内的官方 v0.5.20 反向检查，当前源也通过。目前只有 Gumbel sampler `b07c939d0f55`、Mamba deferred-init `12593d20ead3` 两条达到此证据强度。
- **当前共享源码已覆盖**：有明确冻结源对应实现或完整反向补丁验证。覆盖某项行为不等于整个模型已接受。
- **需增量**：确认当前源缺少历史模块/行为，或明确未合入的模型/native 支持链；其中有些应落 common，具体见 JSON 的 integration_scope，不能机械每模型复制。
- **待语义验证**：存在 common 对应实现或上游结构变化，但原历史回归的等价关系还未闭合。反向 patch 失败本身不是“缺失”的证明，也不得按文件名/提交标题宣布已覆盖。

本次对 100 份历史导出逐项核对 SHA256，逐项执行只读当前源反向检查，67 份 legacy 还使用独立临时 Git index 对官方基线检查；冻结源与其 index 未改。JSON 列出110个来源记录：legacy67、Kimi7、DS26、GLM10（后者是九个逻辑增量+ACK测试修正）。不是要求永久维护110个patch或110条PR。路径列表在JSON最多展示前六项并保留总数；完整源 commit/原 patch 才是权威路径集。

## 当前确认的跨模型整理规则

1. Kimi chat-close 不重复叠到 common response helper；request-owner 原对象身份保护是 428 的真实缺口。DCP/physical page continuation、SSM checkpoint、storage quota/prefix 均保留模型/拓扑前提。
2. GLM completed-chunk core 已在 `8efd135647f8`；Kimi/DS 的 backend/no-buffer/no-linker residual guards 需合一次。DS `5ad27e1d` reasoning cap 与 `1e645a80fb0e` 同行为；它扩大到所有 OSError 的 media client error 分类与 common `6a673233e9f7` 保留 OS faults 的原则冲突，不能照搬。
3. DS `437b982abfdf` 的全局 Pydantic/protocol monkeypatch、stream usage、整数effort1–100 必须由模型 capability/config 选择。已有 native reasoning-exclude 不再包一层 wrapper。DS Rust multimodal + radix-tree native ABI、compress-ratio/mxfp4/routed weights 与 bitmap 支持是一条闭合依赖链，不单独 cherry-pick bitmap。原 native build pins/ABI材料见 source-profile inventory；无法从源存在推导最终镜像已合格。
4. engine 428 的 GuidanceBackend 缺 allocate/move/apply，而 ReasonerGrammarBackend._wrap_grammar 仍取三个 callback；host mask pinning 和 typed completion_tokens_details 也是确认缺口。独立后继 common 源现固定为 commit `1db913dd7b389922243a76caf61bac1c344b3162`、tree `530b9c4618f336340ca7370c742e43583c844655`，包含三个共享增量；尚未 Linux 验证，未计入 428 已覆盖。
5. Qwen GGUF loader/vision/Q8_0 只按 architecture/load-format/tensor-format 启用；Gemma/Qwen2.5 使用同旧镜像不能据此宣称需要或执行 Qwen GGUF 路径。Muse native parser/template 与 Nemotron literal/special-token、Marlin、BREAKABLE 条件独立保留。
6. XGrammar 历史0.2.1源码 `5b4e9ce9e72524037ae24ecd831b9b6604d2eb48` 与0.2.6源码 `bc09a30ec10ba30a6c1ab0c79eaeba3ca518d11f` 不可同装为一个包；语义移植到最终一个固定版本并跑原回归，保留Apache-2.0归属。没有证据要求为此建立每模型整套发布管线。

## 证据来源与范围

后继源增量补记（不计入428）：Kimi selector 固定 commit `02558c2aaab1b1e91a15a8352659bba489dd5ff0`、tree `12b9bdd3308e36d38d1aad10e767a6624e590f14`；Muse selector 固定 commit `109089bac878e6a67224dad900a96d0c3556fb41`、tree `7a76873eccad5b9942952e5ae25b609195a941de`。两者都从 428 选择同一组三个 common 增量，再分别叠加必要 model guard，并已通过 clean Git-index tree 复现；尚未 Linux/模型运行验收。DS后继依赖清单另见本次维护任务的 `DS_NEXT_CANDIDATE_DEPENDENCIES.md`；不能以当前 Python-only recipe 包装102文件/native closure 或把 bitmap 单项当全部支持。

- Legacy完整导出：[patch commit083fe0f](https://github.com/Phala-Network/sglang-serving-patches/tree/083fe0f9728b05a68481ecace7681c2315031ab2)，67条source delta字节等价、六个历史selection全树重构；CI run35491444067、7 verifier和12 wheel检查。历史Compose来源 `2e16dfd8ab1b433e549fb1dc7cdd200dbd326bbd`。这仅是v0.5.19旧组合证据。
- Kimi：[patch commit9964d2](https://github.com/Phala-Network/sglang-serving-patches/tree/9964d2ce342a248b655ffa884fca646be33eb1db)，原composed tree25a790a2、192 CPU、36 CUDA pass/22 skip、CI35491021046/35491018648。Governor未启用，不把其测试移植为新组合接受。
- DS：[patch commit454b2e2](https://github.com/Phala-Network/sglang-serving-patches/tree/454b2e27879858daf6693a6dd0d3f541eee4447b)，classified source b6a5ec4 与实际测试runtime source9acba212全树1fa53db3相同；26patch/source/parent/whole-tree验证，CI35492247269。1M cold/warm/bitmap机制证据可保留，但协议4/7 target-only、48/54 sorted-wire或40/54 ordered-wire都不是全协议PASS；dense workspace OOM仍是独立未解问题。测试工具wire-order增量 `f1297c89dc77115072c85720d39ae91342c8bcc3` 不改变runtime。
- GLM：[source d3c8af2](https://github.com/Phala-Network/sglang/commit/d3c8af2c2800970b17b97a03d0ec9d051ccedd53)，来源映射与当前commit详列下表；428冻结源记录177 XML cases、另GLM66 unittest+22SSD含2rank CPU Gloo，证据归档SHA `d35716c93541b16c06f20aff1b1043a3c11ea1857701899f9c068c13eff7a587`。最终镜像/真实GPU模型测试另算。

未查询或修改线上服务；模型/CVM表来自2026-09-20 handoff的**历史快照**，不是当前在线状态核实。测试结果仅引用原证据范围，不重写失败、不重复大GPU实验。

## 逐来源记录

完整source commit、parent、patch SHA、原始路径、当前检查与后继候选边界见同目录 [COVERAGE.json](COVERAGE.json)。

| 记录 | 历史功能 | 分类 | 当前源对应/注意事项 |
|---|---|---|---|
| [legacy-5404f7600755](https://github.com/Phala-Network/sglang/commit/5404f76007558048d16a458743fcc48afce37cc9) | Fix Qwen3.5 GGUF loading on official SGLang v0.5.19 | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-d67e821bd5ea](https://github.com/Phala-Network/sglang/commit/d67e821bd5ea95286a0f3d7896b6d46f41032df6) | Audit GGUF load completeness by shared parameter identity | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-ea31b4a3509f](https://github.com/Phala-Network/sglang/commit/ea31b4a3509f09f9b91203d6e88b5bcd6d929926) | Preserve Qwen tool argument schemas and complete streaming calls | 需增量（见作用域） | 514fcaf8c5a6, c19e475e65b7 |
| [legacy-79e215cde60b](https://github.com/Phala-Network/sglang/commit/79e215cde60b968c002c8b819845c1c42e1a4f60) | Supply llguidance mask callbacks to the reasoning wrapper | 需增量（见作用域） | 见 JSON 的 engine_location / reason；落 common |
| [legacy-e26b9f4dae32](https://github.com/Phala-Network/sglang/commit/e26b9f4dae3205e280ae032f78dba468dd2b1dd5) | Preserve local schema reference roots for named tool choice | 待语义验证 | c19e475e65b7, 7884e393ddae |
| [legacy-f80677f937c5](https://github.com/Phala-Network/sglang/commit/f80677f937c580a3a55a568df1f65313190d2ca6) | Honor checkpoint mode-specific sampling defaults and explicit overrides | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [legacy-2b2584575aa5](https://github.com/Phala-Network/sglang/commit/2b2584575aa53702ce331c60a70f96b038610665) | Add audited Qwen3.5 GGUF vision projector loading | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [legacy-c4afa9828243](https://github.com/Phala-Network/sglang/commit/c4afa982824346428c8b6b90b7d241cec487da9d) | Use tensor-core BF16 GEMM for large Q8_0 prefills | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-82da9278e229](https://github.com/Phala-Network/sglang/commit/82da9278e229402abcb50b46ee5a57e801bb651c) | Backport upstream 35255 dispatched request cancellation repair | 待语义验证 | 0bf1ed94ed6e, 35fc03abe0b8 |
| [legacy-cc713697cb1b](https://github.com/Phala-Network/sglang/commit/cc713697cb1b4bc38bca7d820facc48483d6f2e0) | fix(openai): harden Qwen3 tool calls and structured output | 待语义验证 | 83b69e75e77b, 514fcaf8c5a6, abdd4d766e02 |
| [legacy-ac6e301b2c45](https://github.com/Phala-Network/sglang/commit/ac6e301b2c453425578fd4f7af5c8a84aba19709) | fix(openai): normalize Qwen3.5 system messages | 待语义验证 | 348b3066f561 |
| [legacy-da8da902526c](https://github.com/Phala-Network/sglang/commit/da8da902526cee378ed317384247e349c1d2c7f0) | fix(openai): preserve Qwen3.5 reasoning tool history | 待语义验证 | 348b3066f561 |
| [legacy-7dd1e4933610](https://github.com/Phala-Network/sglang/commit/7dd1e4933610164e580140caa9dd1f8b7c556c6b) | fix(openai): differentiate Qwen3.5 reasoning effort tiers | 待语义验证 | 348b3066f561 |
| [legacy-7e4e69f5850f](https://github.com/Phala-Network/sglang/commit/7e4e69f5850f829dc9bd65feebaddd0796056987) | fix(openai): enforce Qwen reasoning effort ranges | 待语义验证 | ffcf7799ff22, 348b3066f561 |
| [legacy-6d6103699ea4](https://github.com/Phala-Network/sglang/commit/6d6103699ea407e062adecf6021eebd1c88c66dd) | fix(openai): honor disabled nested reasoning | 待语义验证 | ffcf7799ff22 |
| [legacy-96cd94344d57](https://github.com/Phala-Network/sglang/commit/96cd94344d57257cb4c0d4eea9a3a4b5f1716bf5) | perf(openai): skip unbounded Qwen strict grammar | 待语义验证 | 348b3066f561 |
| [legacy-d61efbc4c4f5](https://github.com/Phala-Network/sglang/commit/d61efbc4c4f5a647dc3026efd28bc1a658226a7b) | fix(openai): drop orphan streaming tool deltas | 待语义验证 | f3418d51a0cd |
| [legacy-47d684c188fd](https://github.com/Phala-Network/sglang/commit/47d684c188fdbbb37423250e6ae2f466511da3cf) | fix(openai): finalize Qwen tool result turns | 待语义验证 | 348b3066f561 |
| [legacy-27487759d660](https://github.com/Phala-Network/sglang/commit/27487759d6602164066d44534d86cd29de7d74ea) | fix(openai): bound default Qwen reasoning | 待语义验证 | ffcf7799ff22, 348b3066f561 |
| [legacy-c0b47b4d9a80](https://github.com/Phala-Network/sglang/commit/c0b47b4d9a80fca2a89a36c2ca9e9d914e1d61e1) | fix(openai): restore Qwen reasoning quality budget | 待语义验证 | 348b3066f561 |
| [legacy-b69731aa5a70](https://github.com/Phala-Network/sglang/commit/b69731aa5a706b4a23414fbf24db26bae4c6c228) | fix(openai): preserve reasoning visibility contract | 待语义验证 | ffcf7799ff22 |
| [legacy-a17450df7fe0](https://github.com/Phala-Network/sglang/commit/a17450df7fe0c2a160517205101a02effe946c85) | Fix: abort handling for dispatched requests after client disconnect (#35255) | 待语义验证 | 0bf1ed94ed6e, 35fc03abe0b8 |
| [legacy-0b21f9af0f2f](https://github.com/Phala-Network/sglang/commit/0b21f9af0f2ffdd2fd7175c0ecae1e86e39e793f) | [Performance] Optimize Qwen3.5 GDN prefill projection layouts (#36267) | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-223e067187a6](https://github.com/Phala-Network/sglang/commit/223e067187a63e72fd8fa854da8bd858eca95dea) | test(qwen38): adapt Phala fixtures to runtime config bags | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-29f0b04675b4](https://github.com/Phala-Network/sglang/commit/29f0b04675b4dd1fececfc25acb134a14b0bc94a) | test(openai): complete Qwen reasoning fixture | 当前共享源码已覆盖 | 见 JSON 的 engine_location / reason |
| [legacy-4dcc87bb9a11](https://github.com/Phala-Network/sglang/commit/4dcc87bb9a11abd98d73f7ee6e2d1199863529e1) | fix(runtime): harden media watchdog and disconnect abort | 待语义验证 | 6a673233e9f7, fd778061bc05 |
| [legacy-119767a19ad0](https://github.com/Phala-Network/sglang/commit/119767a19ad028c45b83b504a3ab20f4acf6d265) | fix(runtime): reject oversized media requests before decode | 待语义验证 | cc703a7a7b40, fd778061bc05 |
| [legacy-58c4ebfd0be5](https://github.com/Phala-Network/sglang/commit/58c4ebfd0be56e8f78f5815c8f20baab32f9c47c) | test(multimodal): exercise eager PIL system-error path | 当前共享源码已覆盖 | 见 JSON 的 engine_location / reason |
| [legacy-66599f0839c0](https://github.com/Phala-Network/sglang/commit/66599f0839c028081f85a3f0bb0ced8bed869918) | test(qwen38): adapt pre-MM fixture to v0.5.19 config bag | 当前共享源码已覆盖 | 见 JSON 的 engine_location / reason |
| [legacy-3852646c7dfd](https://github.com/Phala-Network/sglang/commit/3852646c7dfddcfc875bd4aabb8b5495f85352f6) | fix(qwen3.5): map extended reasoning effort aliases | 待语义验证 | 348b3066f561 |
| [legacy-70bcd26c4621](https://github.com/Phala-Network/sglang/commit/70bcd26c46213cf19dea4ae54e853a78d4240fc8) | fix(qwen3.5): give explicit medium effort a bounded 4096-token budget | 待语义验证 | 348b3066f561 |
| [legacy-17cb69777837](https://github.com/Phala-Network/sglang/commit/17cb69777837cf082db07730da765f617f56b4f1) | fix(openai): normalize null tool schema fields | 待语义验证 | 6efe42ec6a59 |
| [legacy-2a6898f3c996](https://github.com/Phala-Network/sglang/commit/2a6898f3c9964f6e4aa13bce24ad35bfdb412369) | fix(qwen): close empty XML calls and preserve required schema semantics | 待语义验证 | 514fcaf8c5a6 |
| [legacy-fdcb90492c7c](https://github.com/Phala-Network/sglang/commit/fdcb90492c7c85336bd7d879f623dabc8416e208) | build: add CPU-only native wheel qualification target | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-15966fe477b8](https://github.com/Phala-Network/sglang/commit/15966fe477b897ebba322c29d7d9698b31112b67) | test(qwen): exercise normalized request schemas and typed map controls | 当前共享源码已覆盖 | 见 JSON 的 engine_location / reason |
| [legacy-65a1b3f10fd0](https://github.com/Phala-Network/sglang/commit/65a1b3f10fd08d8330384708723d215fbd343b65) | Fuse Nemotron latent MoE projection and shared add (#30430) | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-b07c939d0f55](https://github.com/Phala-Network/sglang/commit/b07c939d0f553c410307b5b70f8411a4037431f0) | perf: use Gumbel-max trick in the main sampler to cut decode CPU dispatch (#38117) | 上游已覆盖 | 见 JSON 的 engine_location / reason |
| [legacy-61ab8c2adb9c](https://github.com/Phala-Network/sglang/commit/61ab8c2adb9c252ac3529b7b4a781db0e7ac79d9) | fix(llguidance): pin host vocab masks before async H2D copy | 需增量（见作用域） | 见 JSON 的 engine_location / reason；落 common |
| [legacy-405fa1086fdb](https://github.com/Phala-Network/sglang/commit/405fa1086fdb40d97959ccde22c404e3d3b6748f) | fix(muse): parse required tool calls natively | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [legacy-c5af5ab92184](https://github.com/Phala-Network/sglang/commit/c5af5ab92184f5d29e4c12ac7d8e8cf81fba46a5) | fix(muse-glimmer): backport channel-framed guided decoding boundary | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-7984762a1925](https://github.com/Phala-Network/sglang/commit/7984762a19255c5d87c3f9c626f90a6d0354a97f) | fix(openai): expose reasoning usage in standard details | 需增量（见作用域） | 见 JSON 的 engine_location / reason；落 common |
| [legacy-889dac086485](https://github.com/Phala-Network/sglang/commit/889dac086485d3b29d119e8957ce75de718e199f) | fix(muse): honor OpenRouter tool and history contracts | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-7aad27962602](https://github.com/Phala-Network/sglang/commit/7aad27962602cc89876ca2c3b536a95aa15a46cd) | fix(muse): default structured output to direct final | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-c5052c199e05](https://github.com/Phala-Network/sglang/commit/c5052c199e05166199b3cb01e4e2adc2d4ed3bba) | fix(muse): preserve named choice and v0.5.18 regressions | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-7070885b6c51](https://github.com/Phala-Network/sglang/commit/7070885b6c511f61d8ae2c4787d7d2dc38fd3e9b) | fix(muse): enforce required tool choice | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-2224d5c89971](https://github.com/Phala-Network/sglang/commit/2224d5c899711426210957da0f3ba341f6b6c110) | fix(muse-glimmer): harden tool calls and structured output | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-752cbf71d2fc](https://github.com/Phala-Network/sglang/commit/752cbf71d2fc874d79f0de511265209e15a2ed0f) | Fix mamba radix cache ssm state indexing (#37836) | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-72d09f13ce3e](https://github.com/Phala-Network/sglang/commit/72d09f13ce3e931800377c191eb1724a30c55e0e) | [Fix] Vacuous marker writes in the cache tests, and an undebited Mamba admission slot (#36415) | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-12593d20ead3](https://github.com/Phala-Network/sglang/commit/12593d20ead3dbd9f9c790b6a51f1f4b8c584e5b) | [Bugfix][Mamba] Clear deferred init metadata before speculative decode (#37165) | 上游已覆盖 | 见 JSON 的 engine_location / reason |
| [legacy-66c99cdb3906](https://github.com/Phala-Network/sglang/commit/66c99cdb39069e02a6914a4d67bef8687db757d2) | fix: add opt-in bounded XGrammar JSON whitespace | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-87d669f137cb](https://github.com/Phala-Network/sglang/commit/87d669f137cb4c6bc0273bf175305da335407eca) | fix: qualify pinned XGrammar 0.2.6 schema regressions | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-93a9c811a9af](https://github.com/Phala-Network/sglang/commit/93a9c811a9af21796878628cae1258348708d3f6) | Fix Nemotron native tool boundaries and exact small-object JSON order | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-6928845df367](https://github.com/Phala-Network/sglang/commit/6928845df367fc5e380cd81dc4b37ba2e73461ef) | Bound emitted reasoning usage and preserve exact XGrammar patch bytes | 待语义验证 | 1e645a80fb0e |
| [legacy-ed810727c954](https://github.com/Phala-Network/sglang/commit/ed810727c954b9c1a7bf9f18ea0e858594197c50) | fix: keep truncated Nemotron thoughts out of tool execution | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-01433fd33149](https://github.com/Phala-Network/sglang/commit/01433fd331495d42bb6dac05b5f77c29e46e941d) | fix: withhold unfinished Nemotron tool calls at stream boundaries | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-69743bca633b](https://github.com/Phala-Network/sglang/commit/69743bca633b582d9df2bbb41c3a0f3d09926d41) | fix: align Muse template instructions with constrained JSON formats | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-ed4266b4513f](https://github.com/Phala-Network/sglang/commit/ed4266b4513fd6b23023aed93c00a65eb3fdc434) | fix: pass Muse tool constraints through the actual template call boundary | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-eec6b2e25ee0](https://github.com/Phala-Network/sglang/commit/eec6b2e25ee098d04475e4784caad7b18021393b) | fix: preserve scheduler ownership when Muse requests are cancelled | 待语义验证 | 0bf1ed94ed6e, 35fc03abe0b8 |
| [legacy-5f9f960c28a1](https://github.com/Phala-Network/sglang/commit/5f9f960c28a16bfaef3f20800c30eeee125753aa) | Fix Nemotron structured output contracts and request lifecycle | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-4dbfdf98a4d5](https://github.com/Phala-Network/sglang/commit/4dbfdf98a4d5b1583cdabcf004c158bec3b7ddb7) | fix(nemotron): distinguish literal data from reasoning control tokens | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [legacy-ec6f1c44c8a7](https://github.com/Phala-Network/sglang/commit/ec6f1c44c8a7eccd2cd3587919defad01abf5929) | fix(serving): abort dispatched requests on streaming cancellation | 待语义验证 | 0bf1ed94ed6e, 35fc03abe0b8 |
| [legacy-068de9fd66d1](https://github.com/Phala-Network/sglang/commit/068de9fd66d1a682e9635c8bbe69d77989eea91e) | test: model dispatch ownership in parallel sampling cleanup fixtures | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-6d3d45b55d98](https://github.com/Phala-Network/sglang/commit/6d3d45b55d9882e29daa4d2e11b44f5f2ae097ae) | Fix stable Marlin routing and honor FP32 NVFP4 reduction | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-f97b21d20d93](https://github.com/Phala-Network/sglang/commit/f97b21d20d9334484ea7a447876c433e2770ab07) | fix: bound XGrammar repetition state and compile JSON string FSM blocks | 待语义验证 | 见 JSON 的 engine_location / reason |
| [legacy-f65bb7af2030](https://github.com/Phala-Network/sglang/commit/f65bb7af2030df7e64d091e538c92565d57ea29b) | fix: preserve const-constrained XML tool argument types | 待语义验证 | 514fcaf8c5a6, c19e475e65b7 |
| [legacy-1d8e0a494693](https://github.com/Phala-Network/sglang/commit/1d8e0a49469302f1bf9f80763e7c8d3db99b20c9) | fix: align chunk budget to KV pages | 待语义验证 | c4ce9b560716 |
| [legacy-cfe6dbb89416](https://github.com/Phala-Network/sglang/commit/cfe6dbb89416065555d4a2f0d2260704680136ec) | fix: enable breakable prefill graphs for hybrid layers | 待语义验证 | 见 JSON 的 engine_location / reason |
| [kimi-0001-prefill-seq-cap](https://github.com/Phala-Network/sglang/commit/37d88dc627e4ab0560bc24e2825b912ffc7f3a0e) | Bound prefill graph replay by total sequence length | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [kimi-0002-chat-stream-close](https://github.com/Phala-Network/sglang/commit/6e6e743682adb5449c072879502afbf6bc41f0b5) | Close chat streaming generators on ASGI disconnect | 当前共享源码已覆盖 | 0bf1ed94ed6e |
| [kimi-0003-request-owner](https://github.com/Phala-Network/sglang/commit/5256c3113810f97a156e9847b79f586009cb3c51) | Bind delayed request aborts to their original request owner | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [kimi-0004-mamba-checkpoint](https://github.com/Phala-Network/sglang/commit/bda19ad5a7a3d6044d6825c4f492929ef7d85182) | Align Mamba checkpoint donation to the absolute page grid | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [kimi-0005-file-storage-ownership](https://github.com/Phala-Network/sglang/commit/cf08f42ebf1a0018d0e6768dd0b014ead9afdfed) | Isolate hybrid MLA and Mamba file storage ownership and quotas | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [kimi-0006-restorable-prefix](https://github.com/Phala-Network/sglang/commit/530bf4c75e7fbad0010a47ccc51d968cc10c53c5) | Intersect restorable hybrid cache endpoints across pools and ranks | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [kimi-0007-chunk-write-through](https://github.com/Phala-Network/sglang/commit/b873d248cdfb2ac62e9bbb1d14f45925c152f053) | Back up completed write-through chunks before request completion | 待语义验证 | 8efd135647f8 |
| [dsv41-0014-ue8m0-mxfp8](https://github.com/Phala-Network/sglang/commit/e53312611f87fe7fffa895c1e0259f3f7e665e07) | [Quant] Serve 32-wide-K ue8m0 block-FP8 linears through the FlashInfer MXFP8 GEMMs (#40039) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0018-hicache-completed-chunks](https://github.com/Phala-Network/sglang/commit/f94b624c3e1abf798ca7e0e495a17ca82d9c8dd8) | fix(hicache): back up completed write-through chunks | 待语义验证 | 8efd135647f8 |
| [dsv41-0019-common-service-contracts](https://github.com/Phala-Network/sglang/commit/5ad27e1db0d14d17d920e9040599f20655fbe9df) | fix(serving): isolate common async, usage and media contracts | 待语义验证 | 1e645a80fb0e, 6a673233e9f7 |
| [dsv41-0025-routed-weight-abi](https://github.com/Phala-Network/sglang/commit/6a899fd8296f3b8f6e1a41ace558ed0f7d8b5057) | fix(dsv41): preserve native FlashInfer routed weight ABI | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0001-rust-interfaces](https://github.com/Phala-Network/sglang/commit/5392a7324f23e0f1d960edb2c60e4fd9020978e9) | dsv4.1: Rust extension modules for image preprocessing, KV pool names, and PD bootstrap (#39677) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0002-standalone-kernels](https://github.com/Phala-Network/sglang/commit/6842c9135a8a2af8458f836bb81ac6ff83e33c32) | dsv4.1: standalone kernels and Python wrappers (#39646) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0003-topk-candidates](https://github.com/Phala-Network/sglang/commit/ae829a492f29d50286ca62e524f66bdab7a314b3) | dsv4.1: Top-k kernels and candidate selection (#39648) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0004-communication-kernels](https://github.com/Phala-Network/sglang/commit/2058fb0a106ef3e9a1431f6400d512333643f618) | dsv4.1: communication kernels and wrappers (#39653) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0005-compression-kv-io](https://github.com/Phala-Network/sglang/commit/d25d72a68e5b240851a0b645b98582d7924b540f) | dsv4.1: compression, KV I/O, and metadata kernels (#39652) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0006-candidate-indexer](https://github.com/Phala-Network/sglang/commit/df74a3ed2401723ff865b514f5bba23a5a0164e4) | dsv4.1: candidate indexer library (#39671) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0007-rope-fp4-packing](https://github.com/Phala-Network/sglang/commit/79a3ac5416bfa512b95d7e615c901eaf9dd63482) | dsv4.1: RoPE and FP4 packing kernels (#39656) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0008-hopper-fp8](https://github.com/Phala-Network/sglang/commit/5919a29f559e8a8a83eab1ca8e2e858ff4a07f9e) | dsv4.1: Hopper FP8 matmul kernels and tuning (#39657) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0009-mhc-projections](https://github.com/Phala-Network/sglang/commit/a55765773e792cb3a7dbbf152a0968eb31c74354) | dsv4.1: mHC computation and compensated projections (#39664) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0010-vision-preprocessing](https://github.com/Phala-Network/sglang/commit/d31c3fa098ffd37ff1b3bbe27219eb5f990e030e) | dsv4.1: vision tower and image preprocessing (#39668) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0011-chat-encoding](https://github.com/Phala-Network/sglang/commit/137f96a5cc08d3fd74c5c6cc8055aec73c59af07) | dsv4.1: chat encoding and tool parsing (#39665) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0012-engram-history](https://github.com/Phala-Network/sglang/commit/22d54075f900b0c78d677d8a28d4db855e274c4a) | dsv4.1: Engram module and request history support (#39666) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0013-compress-ratios](https://github.com/Phala-Network/sglang/commit/5648185cee4c1d0dc49525dc50d4bfab0fb9bc95) | [DSV4] Generalize attention metadata, sparse prefill, and KV pool over compress ratios (#39921) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0015-native-integration](https://github.com/Phala-Network/sglang/commit/9af234a4891a8facbe92626a2c54fffce5f04637) | dsv4.1: remaining model and runtime integration (#38798) | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0016-dense-prefill](https://github.com/Phala-Network/sglang/commit/5645663683f25062e10596ac09661d6a169a1993) | Bound DeepSeek-V4.1 dense prefill indexer memory | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0017-dense-prefill-tests](https://github.com/Phala-Network/sglang/commit/3c0eb7c73d9c51baf236faebd649ea14c6482ecb) | Strengthen dense prefill consumer correctness and memory tests | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0020-model-protocol-contracts](https://github.com/Phala-Network/sglang/commit/437b982abfdfa1b563122e061ead1a1cd1211c29) | fix(dsv41): isolate model reasoning, roles and async opt-in | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0021-medium-finalize](https://github.com/Phala-Network/sglang/commit/ecd9f93317e41aa19487948ddab05f754556a990) | perf(dsv41): isolate medium target finalize plane | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0022-transplant-closure](https://github.com/Phala-Network/sglang/commit/7a23a97622a8483f3fe6f1e6d37e06bcd933aa27) | fix(dsv41): close stable transplant imports and document qualification boundaries | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0023-mxfp4-padding](https://github.com/Phala-Network/sglang/commit/81b67d8f1736b387aff2f908a2cddf011803367a) | fix(dsv41): restore MXFP4 padding before weight shuffle | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0024-protocol-selftest](https://github.com/Phala-Network/sglang/commit/127a3646891cdefc09b1d59cf1a7fb11e4f23f12) | test(dsv41): use current reasoning parser in protocol selftest | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [dsv41-0026-candidate-bitmap](https://github.com/Phala-Network/sglang/commit/b6a5ec4af0f7981cab954de9a5f4e9ad16fd6948) | fix(dsv41): size candidate bitmap for speculative scratch extent | 需增量（见作用域） | 见 JSON 的 engine_location / reason |
| [glm-atomic-tools](https://github.com/Phala-Network/sglang/commit/0317dda785acf89c934e7a26327ab48f72c92edb) | Publish GLM tool calls atomically after the closing marker | 当前共享源码已覆盖 | 2d12271ad4d2 |
| [glm-reasoning-usage](https://github.com/Phala-Network/sglang/commit/09c9094d197fc5021533a9541df75593e84c196f) | Cap reported reasoning tokens at the completed output length | 当前共享源码已覆盖 | 1e645a80fb0e |
| [glm-dsa-host-budget](https://github.com/Phala-Network/sglang/commit/6ac0087cbe182df62a871b29905183c60163a823) | Account DSA host startup allocations and enforce requested hugepages | 当前共享源码已覆盖 | 9e020f0cdf30 |
| [glm-idle-dp-gauge](https://github.com/Phala-Network/sglang/commit/f5b2896f4b7cc64997eb999ca54e7646c89b9d0e) | Refresh an idle local running gauge without resetting token counters | 当前共享源码已覆盖 | e84bb2a5c817 |
| [glm-mooncake-ssd-ranks](https://github.com/Phala-Network/sglang/commit/5131ac5344737595ca9aa7cd794247f210583ba7) | Isolate Mooncake SSD directories by physical worker rank | 当前共享源码已覆盖 | f7a7d6333a01 |
| [glm-completed-chunks](https://github.com/Phala-Network/sglang/commit/05b7ae76048eace20a32481af5669b63935cc6d2) | Back up completed write-through chunks after rotation acceptance | 当前共享源码已覆盖 | 8efd135647f8 |
| [glm-flashinfer-cleanup](https://github.com/Phala-Network/sglang/commit/76d35078fa769bd340104a6a06e5b412fc29696c) | Preserve the external FlashInfer workspace cleanup overlay | 当前共享源码已覆盖 | 2f96c6101950 |
| [glm-physical-kv-budget](https://github.com/Phala-Network/sglang/commit/d9651dc87c1eb15ef91b9d9cd10f02f1b8db3140) | Bound chunk continuation by physical KV capacity | 当前共享源码已覆盖 | c4ce9b560716 |
| [glm-host-async-ack](https://github.com/Phala-Network/sglang/commit/c09bbad9c98f9ee3a14ca3b8992e8f687816cf95) | Preserve guarded host-only async ACK and spawn-safe tests | 当前共享源码已覆盖 | 5bae612858ac |
| [glm-host-async-ack-spawn-test](https://github.com/Phala-Network/sglang/commit/d3c8af2c2800970b17b97a03d0ec9d051ccedd53) | Preserve guarded host-only async ACK and spawn-safe tests | 当前共享源码已覆盖 | 5bae612858ac |
