# AI Coding Agent 的高频 Issues、核心瓶颈与工程化解决方案

**2026 年深度调查与工程实施报告 · v2.0（逐项解决方案扩展版）**  
**资料截止日期：2026-11-17**  
**研究对象：** 从需求理解、代码库检索、计划执行、工具调用、代码修改、测试、Review、CI/CD、发布到生产维护的 Coding Agent 全流程。  
**本次更新：** 将 16 类 Issues 扩充为解决方案比较、实施步骤、工具选型、风险边界、故障注入与验收标准；新增 20 项一方技术参考。  
**报告定位：** 同时回答“哪些问题最常见”和“哪些问题损失最大”，并给出可复用的治理架构、技术方案和验收路径。

> **核心结论**：当前主要约束不再是“能否快速写出代码”，而是“是否理解真实要求、能否在复杂仓库中保持正确状态、能否经过独立验证，以及能否在严格权限边界内完成真实交付”。应采用 **Verification-first、Evidence-driven、Policy-enforced** 的生产架构。

## 0. 执行摘要

- **最常见的开发者痛点**：2026 Stack Overflow 调查（本题 n=13,648，多选）中，69.3% 报告“看似合理但错误的代码”耗费时间，54.2% 指出生成代码难以审查，49.3% 指出缺乏上下文，45.1% 遇到虚构依赖包/配置。[R01]
- **最常见的工具工程缺陷**：对 Claude Code、Codex CLI、Gemini CLI 的 3,864 条已关闭、核实的 Bug 研究显示，功能性缺陷占 67.0%，API/集成错误占根因的 21.4%，配置/安装问题占 15.9%；工具/API 编排层和命令执行层分别涉及 37.6% 与 25.0% 的 Bug。[R02] **此口径不是模型生成代码错误率**。
- **最大质量瓶颈**：测试通过不代表业务正确或安全。需求定义和部署模型之间存在差距；验收测试可能过窄、过严、与文字需求矛盾，甚至被 Agent 规避。[R04][R05][R14]
- **最大长周期瓶颈**：连续修改有状态代码库时，错误会累积。ChainSWE 在 54 个 Python 仓库、304 个关联 Issue 的任务集上观察到随任务链加深、相对于单 Issue 设定最高约 70% 的性能下降；这不是所有生产环境的统一下降比例。[R06]
- **最大风险瓶颈**：不可信 Issue/PR/仓库文档可能被当成指令，加之工具或执行器拥有密钥、写入/发布权限，造成信息泄漏与供应链入侵。[R09][R10]
- **最大运营瓶颈**：写代码节省的时间可能被代码审查、追责、测试和返工吞噬。DORA 2025/2026 把 AI 视为组织能力的放大器；不能只统计生成 Token、代码行数或 PR 数。[R08]

**建议优先级**：P0 建立结构化任务契约、独立验收、受控沙箱、证据化终态；P1 建设仓库上下文/环境可复现/断点恢复/Review 工具链；P2 优化多 Agent 并发、路由和长期运维。

---

## 1. 方法论与证据口径

### 1.1 四类证据不能混算

| 类型 | 研究对象/分母 | 能支持什么结论 | 不能支持什么结论 |
|---|---|---|---|
| 开发者问卷 [R01] | 13,648 名回答特定多选题的受访者 | 哪些 AI 使用问题令开发者耗费时间 | 单次 Agent 运行的精确故障率、因果关系 |
| 工具 Issue 研究 [R02] | 3,864 条经过筛选的已关闭 Bug | Agent CLI/运行时/集成层最常见的工程缺陷 | 生成补丁的质量、全部用户的实际发生率 |
| 任务/仓库基准 [R04][R05][R06] | 给定任务集、模型、脚手架和验证器 | 特定受控设置中的任务表现与失败模式 | 所有公司、所有模型的生产效果 |
| 代码与安全研究 [R07][R11][R12] | 已合并 PR、代码样本、特定 CWE 测试 | 代码质量、安全审核与维护风险 | 自动推导 AI 是某项趋势的唯一原因 |

**证据等级（本报告自定义）：** A = 大样本原始调查/明确可复现数据；B = 已发表或具完整方法的实证研究；C = 安全研究团队公布的事件/实验复现；D = 框架性论文或厂商观察性分析。等级不是研究质量的官方评分。

**本报告的 P0/P1/P2 是工程风险优先级，不是行业公开统计的出现频率排名。** P0 表示一旦缺失控制，可能使交付真实性或安全性不可接受；并不意味着发生次数一定最多。

### 1.2 2026 年最常见的耗时问题：原始调查

**来源 [R01]：Stack Overflow Developer Survey 2026；多选，n=13,648。**

| 排名 | 开发者报告的耗时问题 | 占该题受访者比例 | 生产链影响 |
|---:|---|---:|---|
| 1 | 看似合理但错误的代码 | 69.3% | 需求、实现、验收 |
| 2 | 生成代码难以 Review | 54.2% | Review、合并 |
| 3 | 缺少必要上下文 | 49.3% | 仓库检索、设计 |
| 4 | 虚构依赖包或配置 | 45.1% | 环境、工具、供应链 |
| 5 | 内部知识错误或过时 | 38.7% | 项目规则、历史决策 |
| 6 | 过时 API | 33.9% | 外部集成、维护 |
| 7 | 低效调试路径 | 24.7% | 修复循环、成本 |
| 8 | 安全或隐私问题 | 23.5% | 安全与合规 |
| 9 | 许可证/来源不明确 | 11.4% | 依赖、审查、法务 |

> **解释**：这是“受访者在过去一年哪些错误最耗时间”，不是“69.3% 的生成代码都是错的”；多选结果不可相加。

### 1.3 Coding Agent 工具本身的工程缺陷：3,864 个 Bug

**来源 [R02]：对 Claude Code、Gemini CLI、Codex CLI 的公开 Issue 人工编码；截止 2025-12-12。** 三者分别分析 2,343、329、1,192 条 Bug。研究剔除了重复报告与非真实缺陷，具有人为标注和选择偏差；其公开 PDF 仍含出版格式占位信息。

| 观察维度 | 主要统计 | 含义 |
|---|---|---|
| Bug 类型 | 功能性 67.0%；UI/可用性 17.9%；兼容性 7.6%；性能 5.9%；安全 1.7% | 高危安全事件不一定高频，但损失可能极高 |
| 根因 | API/集成 21.4%；配置/安装 15.9%；交互/UI 11.1%；环境/平台 10.5%；AI 逻辑/行为约 10.0% | 不能把所有故障归咎于模型推理 |
| 用户症状 | API/通信 18.3%；终端 14.0%；命令执行 12.7% | 多数缺陷体现在真实工具操作边界 |
| 故障位置 | 工具/API 编排 37.6%；命令执行与监控 25.0% | Tool Gateway 和 Runtime 应成为重点质量对象 |

## 2. 风险排序：出现频率与破坏程度分开评估

| 编号 | 瓶颈/Issue | 经验频度 | 影响 | 风险级别 | 主要控制层 |
|---|---|---|---|---|---|
| I01 | 需求含糊、业务逻辑不一致 | 高 | 高 | P0 | 任务契约、验收 |
| I02 | 测试绿色但实现错误 / 漏掉边界 | 高 | 极高 | P0 | 独立验证器 |
| I03 | Prompt Injection / 密钥和供应链 | 非均匀、难量化 | 极高 | P0 | 沙箱、权限、可信边界 |
| I04 | 自报成功、实际未合并/未部署 | 中 | 极高 | P0 | 状态机、外部证据 |
| I05 | 仓库上下文缺失/过时 | 高 | 高 | P1 | 检索、符号索引 |
| I06 | 工具调用、协议/参数/CLI 失败 | 高 | 高 | P1 | Tool Gateway、重试策略 |
| I07 | 依赖与环境不可复现 | 高 | 高 | P1 | 容器、锁文件、基线镜像 |
| I08 | 长任务状态漂移、修复循环 | 中高 | 高 | P1 | Checkpoint、预算 |
| I09 | 大 Diff/重复代码/Review 负债 | 高 | 高 | P1 | Diff Budget、静态质量门禁 |
| I10 | 数据写入/事务/并发/状态一致性 | 中 | 高 | P1 | 集成/E2E/性质测试 |
| I11 | 多 Agent 并行冲突 | 随并发增加 | 高 | P1 | Worktree、接口契约 |
| I12 | PR 与发布链路权限/状态错配 | 中 | 高 | P1 | CI、Branch Protection |
| I13 | 成本、速率与资源失控 | 中 | 中高 | P1 | 配额、模型路由、缓存 |
| I14 | Benchmark 偏差/测试污染 | 评估系统内常见 | 高 | P1 | 私有/滚动 Evals |
| I15 | 文档与项目知识漂移 | 高 | 中 | P2 | Docs-as-code |
| I16 | 可观测性、复盘数据缺失 | 中高 | 高 | P1 | 事件日志、Trace、SLO |

注：“经验频度”是综合多个来源后的定性判断，不是从公开数据计算出来的统一统计量。

## 3. 根因模型：为什么单点能力提升无法转化为端到端交付？

### 3.1 两个根本落差

2026 年的研究提出“需求落差（Requirement Gap）”与“环境模型落差（Model Gap）”：[R15]

1. **需求落差**：用户的真实意图无法被 Issue、Prompt 和测试完全表达。典型症状是“功能看起来正常，但业务规则错了”。
2. **环境模型落差**：测试环境只是部署世界的近似；网络、权限、并发、数据量、外部 API、浏览器和配置会带来差异。典型症状是“CI 通过，但线上出问题”。

由此产生第三类衍生落差：**证据落差**。Agent 的文字解释、测试声称与真实 Git/CI/CD/线上状态不一致。

### 3.2 复杂任务失败会累积

如果一个流程有 n 个关键关口、各关口独立正确率均为 p，完全成功率简化为 p^n。以 p=0.95、n=10 为例，结果约 59.9%。这只是说明性数学模型，**不是 Agent 的实测成功率**。真实工程中的错误往往高度相关，且上游错误会放大下游风险。

ChainSWE 连续 Bug 维护研究验证了这一方向：100 条任务链、304 个 Issue、54 个 Python 项目，模型在更深的依赖链上较单 Issue 条件有明显退化，上限约 70%。[R06]

### 3.3 出错最危险的三个接口

- **人 → Agent**：需求、授权、验收标准与非目标没有结构化。
- **Agent → 工具/代码库**：错误工具、无效参数、过期文档、不完整上下文和不可重现环境。
- **Agent → 生产**：验证器、权限和发布事实缺失，产生虚假成功或隐蔽漏洞。

---

## 4. 十六个关键瓶颈：机制、症状、处理与验收

### I01｜需求理解和业务逻辑偏差（P0）

**典型症状**：做出了能点击的界面，但数据没有落库；支付/退款只覆盖正常路径；缺少幂等、权限、重复请求、事务边界；用户要求重构，Agent 却改变了业务行为。Columbia DAPLab 在 15+ 应用、5 类 Coding Agent 工具中记录了九类高影响失效，其中业务逻辑不一致是突出类别。[R03]

**根因**：需求只描述效果，不包含不变量、边界、反例和可测的完成定义；Agent 把默认假设当成事实。

**方案**：
1. Issue 必须包含目标、非目标、输入输出、错误路径、验收测试、风险等级、允许变更路径。
2. 关键业务先写 Business Invariants（例如退款累计额不得大于已支付额），再写代码。
3. 对含糊需求建立 `BLOCKED_SPEC` 状态；允许在明确安全边界内继续低风险工作，不允许把假设伪装成验收事实。
4. 让独立 Reviewer 对照需求和 Diff，重点检查遗漏，而非只判断代码风格。

**验收指标**：Business Invariant Coverage、需求变更率、验收缺陷率、需求澄清导致的返工时长。

### I02｜测试通过但实际错误，验证预言机不可靠（P0）

**典型症状**：Agent 自己写了浅测试并让测试通过；隐蔽状态变化未覆盖；恶意或错误修改影响了验证代码；“正确代码被坏测试拒绝”和“错误代码被漏测放过”同时存在。

**实证**：OpenAI 2026-07 对 SWE-bench Pro 的审计估计约 30% 任务存在问题，包含不合理严格测试、需求描述不足、低覆盖测试和误导性 Prompt。[R04] 2026-09 的 SWE-Bench Pro V2 从旧版 731 个公开任务中剔除 89 个无效任务，并修订 69 个“说明与测试矛盾”的任务文本；还新增干净环境复评以减少绕过验证器的问题。[R05]

**方案**：
1. 验收标准由任务发起方、独立测试人员或历史可信规范提供，不以 Coder 新增测试作为唯一判据。
2. 建立 Fail-to-Pass、Pass-to-Pass、Boundary/Negative、Property-based、Integration/E2E、Security 六类验证层。
3. 将测试结果与 `base_sha`、`head_sha`、依赖锁文件哈希、镜像摘要、测试集版本绑定。
4. 在干净环境再次验证 Agent Diff；禁止通过修改测试、Harness 或依赖缓存作弊。
5. 关键业务再使用灰度和线上不变量监控，弥补测试与真实场景差距。

**验收指标**：Accepted-but-Wrong Rate、Escaped Defect Rate、False Pass/False Fail、Invariant Coverage、Clean Re-grade Difference。

### I03｜安全边界破坏：Prompt Injection、密钥和供应链（P0）

**威胁路径**：攻击者控制 Issue/PR/README/工具响应 → 内容进入 Agent 上下文 → Agent 把它当成权威指令 → 利用 Read/Shell/GitHub/网络工具读取密钥、写恶意内容、提交 PR 或发布包。

**真实研究案例**：微软 2026-06 报告发现 Claude Code GitHub Action 的 Read 路径在特定环境下可受不可信 GitHub 内容诱导读取 `/proc/self/environ`，导致 Runner 环境变量中的密钥暴露风险；相关敏感 `/proc` 文件访问后来被修复。[R09] 这说明仅对 Bash 做环境清理远远不够。

**方案**：
1. 不可信文本只作为数据处理，不得获得工具授权和系统指令身份。
2. 把读代码、写补丁、推送 PR、合并、部署划分为独立的机器身份与权限域。
3. 使用短期令牌、最小权限、无生产密钥的 PR 沙箱、文件系统和出站网络限制。
4. 对 `.github/workflows/**`、依赖锁文件、包发布配置、身份鉴权代码等设置高风险变更审批。
5. 对第三方 Skills/MCP/仓库配置执行供应链签名、来源固定、脚本静态审查和安全隔离。
6. Prompt 层防护只能作为补充；必须由工具网关/OS/container/CI 权限机制强制执行。

**验收指标**：未经授权的工具调用次数、敏感文件读取阻断率、异常出站连接数、令牌权限范围、红队注入成功率。[R10]

### I04｜假成功：Agent 自述、真实交付状态和用户观感不一致（P0）

**典型症状**：“已经合并”但 PR 仍 Open；“已上线”但工作流失败；“已上传”但用户找不到产物；“修复完成”但没有运行验证；UI 展示成功但后端没有持久化。[R13]

**根因**：Agent 将意图、工具调用、工具返回和外部最终状态混为一谈；失败日志被截断或转化为流畅的自然语言总结。

**方案**：
- 强制状态机：`QUEUED → RUNNING → VERIFYING → REVIEWING → PR_OPEN → MERGED → DEPLOYED → VERIFIED`；独立的 `BLOCKED/FAILED/ROLLED_BACK`。
- 所有终态由 Git provider、CI、部署系统和运行健康检查返回的可核验字段决定。
- 输出报告包含 PR URL、Commit SHA、CI Run ID、artifact digest、部署环境、验证时间；缺项填 `NOT_VERIFIED`。
- 失败不得自动吞掉；禁止以模型主观评价覆盖外部事实。

**验收指标**：False Completion Rate、Orphaned Artifact Rate、Trace Completeness、可追溯 PR/Deploy 比例。

### I05｜大型仓库上下文不足与知识陈旧（P1）

**典型症状**：修改错误实现位置；遗漏消费者/接口/配置；根据过时 `README` 构建；已有功能重新写一遍；错误地假设仓库不存在某个模块。

**根因**：Context Window 被无关日志占据、检索缺少结构化代码信息、符号/依赖/运行配置漂移、文档无版本约束。

**方案**：分层上下文：全局安全策略 → 项目规则（AGENTS.md）→ 任务相关符号/调用链 → 最近变更与测试 → 按需 Skills；代码检索以 `rg + LSP/AST + repo map + dependency graph` 为基础。对 API 文档保留版本、检索时间与链接；针对关键断言要求出处或代码定位。

**验收指标**：Top-k Relevant File Recall、Unnecessary Read Ratio、错改文件比例、Context Token/Accepted Task。

### I06｜工具调用错误、CLI 与协议集成脆弱（P1）

**典型症状**：调用不存在的工具、参数 schema 不符、429/超时、命令被截断、Shell 转义问题、错误路径、工具返回不可解析、权限配置语法不兼容。[R02]

**方案**：
- 建立 Tool Gateway：JSON Schema 参数校验、工具允许列表、权限判定、超时、重试策略、幂等键。
- 区分可重试错误（429、短期连接失败）和不可重试错误（权限不足、错误 schema、缺少目标资源）。
- Shell 命令尽量使用模板化、参数化调用；高风险命令不得靠自然语言“禁止”保护。
- 对不同执行器提供 Adapter，不能把某一 Agent 的 YAML 权限配置机械复制到另一 Agent。
- 所有错误返回 `error_code + retryable + stage + source`，避免模型凭空猜测原因。

**验收指标**：Tool-call Success Rate、Schema Error Rate、Repeated-tool-loop Rate、Retry Amplification。

### I07｜构建环境和依赖不可复现（P1）

**典型症状**：Agent 本地通过，CI 失败；Node/Python/Rust/编译器版本冲突；平台差异、动态依赖漂移、外部服务不可用；虚构包名或 API 引发安装失败。[R01][R02]

**方案**：基线容器或 Devcontainer、锁定依赖、基础镜像 digest、最小可运行 seed 数据、离线构建缓存、服务 Mock 与真实集成环境分层；执行前提供 `baseline_pass`，将环境已有失败与 Patch 新增失败分离。

**验收指标**：Reproduction Rate、Baseline Failure Rate、Environment Drift、Cold-start Time。

### I08｜长任务状态丢失、目标漂移和无限修复循环（P1）

**典型症状**：先前承诺的约束忘记了；重复读同一文件；失败后不断改动无关模块；一次修复破坏下游；上下文压缩丢失关键事实。[R06][R17]

**方案**：任务分阶段，每阶段有显式交付物；Git Checkpoint、任务状态持久化、事件日志；任务预算（Token/时间/工具次数/最多修复轮）；失败后按 root cause 分类处理；达到阈值升级为 `BLOCKED`，不能无限循环。

**验收指标**：Loop Rate、Checkpoint Recovery Success、Scope Drift Rate、Long-horizon Pass Rate。

### I09｜难审查的大 Diff、重复代码和技术债（P1）

**典型症状**：添加大量辅助函数绕过既有抽象；重复粘贴；为让测试变绿随意屏蔽异常；修改覆盖面过大且缺少设计说明。

**实证**：2026 年对 1,210 个已合并 Agent Bug-fix PR 的研究发现，不同 Agent 的新增静态质量问题应按代码变更规模归一化；已合并不等于质量合格，常见问题是代码异味。[R07] GitClear 的观察性研究也报告了重复代码增加、代码移动重构减少的趋势，但不能因此断言所有趋势均由 AI 因果导致。[R12]

**方案**：Diff Budget、关联 Issue 的最小修改、重复代码检测、复杂度增量检测、风险目录变更门禁、Reviewer 对架构一致性和异常处理进行独立检查。超过规模阈值先拆 PR，不是简单提高模型预算。

**验收指标**：Changed Lines/Accepted Task、Duplication Delta、Review Minutes/PR、Rework Rate、Maintainability Delta。

### I10｜数据库、前后端状态和并发行为（P1）

**典型症状**：UI 显示“已保存”但数据库未提交；数据状态跨组件不一致；重复回调导致多次扣款；并发执行引发 Race；迁移脚本缺少回滚。

**方案**：业务端到端流程自动化；双重验证 UI 状态与持久化状态；属性/不变量测试；幂等键；事务回滚测试；迁移前影子数据/备份/向后兼容检查；线上一致性监控。Columbia FlowCheck 2026 将“显示成功但数据没有被保存”作为代表性的静默故障。[R13]

**验收指标**：UI↔DB Consistency、Idempotency Pass Rate、Transaction Rollback Coverage、Migration Reversibility。

### I11｜多 Agent 并发冲突（P1）

**典型症状**：共享工作目录导致相互覆盖；两个 Agent 修改同一接口但理解不同；后合并的 PR 与基线不一致；Reviewer 与 Coder 共享同一偏见。[R17]

**方案**：每个任务独立 Worktree/Container，按文件/模块/接口提前分区；接口契约先行；依赖 DAG；合并前必须 rebase 并对实际 Head SHA 重新测试；Reviewer 在独立上下文中审查。并发度按照模块耦合度而不是 CPU 数量来确定。

**验收指标**：Merge Conflict Rate、Rebase Retest Failures、Cross-Agent Rework、Coordination Cost。

### I12｜PR、CI 和生产发布最后一公里（P1）

**典型症状**：提交到错误分支、无仓库写权限、PR Open 但被误报为 Merged、CI 测的不是最后 Commit、自动部署失败而缺少告警。

**方案**：Push/PR/Merge/Release 分开授权；分支保护和必需 Check；CI 检查 `tested_sha==merge_candidate_sha`（按实际合并策略考虑 merge queue 的测试提交）；发布产物使用 digest；灰度与健康检查；生产发布失败自动停更或回滚。

**验收指标**：CI-to-Head Match、Merge Eligibility、Deployment Verification Rate、MTTR/Change Failure Rate。

### I13｜Token、工具调用与人力 Review 成本（P1）

**典型症状**：多个 Agent 重复调查同一个目录；无界推理；大量日志进入上下文；PR 生成更快但审核队列增长；API 费用看似下降而总成本上升。

**实证**：DORA 2026 观察到，代码生成节省的时间经常重新转移到审查验证；METR 2025 的一项随机实验在其研究条件下观察到经验开发者使用当时 AI 工具完成任务反而更慢，METR 2026 说明新实验因受试者选择偏差无法得出当前生产率的可靠估计。[R08][R16]

**方案**：根据任务难度路由模型，针对稳定代码检索缓存，设置 `cost_budget` 和 `fix_attempts`；计算每个“成功验收任务”的模型、计算、Review、返工总成本；建立 Review WIP Limit，避免推送大批未经验证 PR。

**验收指标**：Cost per Accepted Task、Human Review Minutes、Token Waste Ratio、Queue Time、Effective Lead Time。

### I14｜评测污染、指标错置与缺少真实用户反馈（P1）

**典型症状**：基准榜单成绩很高，但真实仓库效果差；测试集曾被训练见过；把通过率当产品质量；只看 PR 数量不看上线缺陷。[R04][R05]

**方案**：内部保密/滚动任务集、相同环境的配对评测、跨模型/版本 A/B、重放轨迹、独立验收、测试集污染检查、线上缺陷反馈；关注任务质量+成本+安全+人力，而非单一 pass@1。

**验收指标**：Verified Resolution、Escaped Defect、Cost/Accepted Task、Benchmark↔Production Correlation、Unexplained Failure Share。

---

## 4A. 十六类 Issues 的现有解决方案：原理、实施步骤、局限与验收（新增）

本章沿用 I01—I16 编号。区分 **立即可用的成熟工程控制**、**需自研集成的生产机制** 和 **仍属研究方向的技术**。工具名称代表可供评估的实现，并不意味着已在本报告所讨论的仓库中安装或运行。建议所有效果指标先记录基线，再以配对任务实验确定改善幅度，不设无证据的“统一行业标准”。

### I01｜需求理解与业务逻辑偏差：任务契约 + 领域不变量 + 需求审查

**诊断与根因。** 自然语言 Issue 往往只描述 UI 现象或 happy path；隐含业务规则（权限、并发、幂等、异常、非功能性指标）未显式化。Agent 会补全“合理假设”，但这种假设未必与真实业务一致。提示词更长并不能保证需求被正确表达。

**现有方案对照：**

| 方案 | 当前可用工具/方法 | 何时选择 | 局限与成本 |
|---|---|---|---|
| 结构化 Issue 模板 | GitHub Issue Forms、JSON Schema、Pydantic | 全部自动化任务入口 | 仍需人确认业务含义 |
| BDD/示例映射 | Gherkin/Cucumber、Given-When-Then、Example Mapping | 用户旅程与领域规则 | 维护场景样例需投入 |
| 契约先行设计 | OpenAPI、Pact 合约测试、类型系统 | API/微服务集成 | 接口正确不等于业务正确 |
| 领域不变量 | 纯函数断言、状态机测试、SQL 约束 | 金额、库存、审批、账号权限 | 不变量是否完整依赖领域专家 |

**推荐实现。** ① 在任务入口要求 `objective/non_goals/acceptance/risk/affected_paths/rollback_owner`；② 将验收标准拆成正常路径、错误路径、边界输入、权限场景、状态持久化和恢复；③ Planner 输出 `assumptions[]`，高影响且未证实的假设进入 `BLOCKED_SPEC`；④ Reviewer 以独立的业务检查表判断“遗漏了什么”，不是仅看是否遵循 Prompt；⑤ 每条验收对应一个可运行测试或可核验的人工步骤。对于支付或退款，至少包含累计金额约束、并发更新与重复请求幂等。

**常见反模式。** 把 Coder 自己生成的验收条件直接作为唯一需求依据；将“能运行”定义为完成；任务开始后随意扩展范围。

**验收与退出条件。** 100% P0 任务有机器可读契约；含糊业务规则明确 BLOCKED；抽查的业务验收与测试一一对应。建立 `Specification Clarification Rate`、`Post-merge Requirement Defect Rate`。**来源：** [R03][R15]。

### I02｜测试绿色但实现错误：多层验证 + 独立 Test Oracle + 变异测试

**诊断与根因。** 覆盖率只测“执行过哪些代码”，不测测试断言是否足够强；Agent 可能把验证器改到全绿，或绕开了非正常路径。评测基准也可能有错误测试与隐藏约束。SWE-Bench Pro V2 的双向校验（参考补丁应通过、空补丁应失败）及干净环境复评提供了可复用的设计思路。[R04][R05][S01]

**五层现成方案。**

| 层级 | 工具与方法 | 重点判据 | 不足 |
|---|---|---|---|
| T0 静态 | Ruff/ESLint、mypy/tsc | 类型、风格、明显错误 | 无法验证业务逻辑 |
| T1 单元/性质 | pytest/Jest、Hypothesis、fast-check | 边界、随机输入、业务不变量 | 必须先设计正确性质 |
| T2 集成/契约 | Testcontainers、Pact、真实 DB 的测试容器 | API、事务、协议、依赖行为 | 环境和维护成本较高 |
| T3 UI/E2E | Playwright、Cypress | 用户旅程、浏览器状态 | UI 测试波动和速度问题 |
| T4 独立复评 | Clean-room CI、隐藏用例、mutation testing | 真实 Head SHA 的鲁棒性 | 昂贵；需防测试集泄露 |

**落地步骤。** ① 保留 `base_sha` 的基线测试结果；② 隔离 Coder 工作区与验收测试资产，危险目录修改强制审查；③ 对关键不变量用性质测试生成负面及边界样例；④ 运行 `fail-to-pass` 与 `pass-to-pass`；⑤ 可对关键模块加入 mutation testing，检查测试能否“杀死”故意植入的缺陷；⑥ 在全新容器对当前 `head_sha` 重跑；⑦ 如果 CI 运行完成后又提交新 Commit，立即废除旧验证证据。

**示例：** Playwright 的自动重试断言适合处理异步 UI，Hypothesis 用于随机性质测试；它们可以提高测试信噪比，但不能代替领域不变量。[S09][S10]

**失败升级。** 测试集与需求冲突、验证器被改写、无法在干净环境复现时标记 `TEST_ORACLE_UNTRUSTED`，不自动合并。

**验收。** 独立验收通过且 `verified_sha == candidate_sha`；至少一次干净环境复评；跟踪 `False-pass Rate`、`Mutation Score`、`Escaped Defect Rate`。

### I03｜Prompt Injection、工具越权与供应链：四层强制安全边界

**诊断与威胁模型。** 不可信 Issue、README、PR 评论、网页、依赖说明、MCP 工具描述都可能包含要求模型执行额外动作的文本。将自然语言“忽略恶意指令”写进 Prompt 只是软约束。OWASP 将输入筛选定位为辅助，不视为安全边界；MCP 安全指引强调最小权限、工具 schema 完整性和短期令牌。[S02][S03][S04]

**推荐控制架构。**

1. **信任分区：** `untrusted_intake` 只读/抽取结构化数据；`coding_sandbox` 不带生产密钥；`review` 获取只读 Diff；`merge` 是独立身份；`deploy` 由受保护环境调用。不得让外部 Issue 内容凭空获得合并授权。
2. **工具网关：** 每次调用同时检查身份、目标仓库、允许路径、命令类别、参数、出站域名、审批范围与变更风险。工具描述与 schema 更新需审计，不能只信任 `readOnlyHint` 等元数据。
3. **OS/运行时隔离：** 每任务无特权容器或 VM，限制文件系统挂载、网络出站、内核能力、进程/CPU/内存。外部依赖安装在受控阶段进行。Codex 官方明确区分 Sandbox（技术边界）与 Approval（审批时机）。[S05]
4. **CI 与供应链：** 无密钥执行不可信 PR；不要在持有机密的 `pull_request_target` 流程中检出并执行不可信代码；固定关键 Actions 版本/来源，检查依赖锁文件；生成并验证制品证明（Attestation/SBOM）。[S06][S07]

**方案选择。** Codex 有 OS 级沙箱与审批控制；Claude Code 有分层权限规则和 Hooks；容器隔离适用于跨 Agent 统一执行。以上机制都需要针对实际版本和平台做拒绝测试，不能仅凭默认行为断言安全。[S05][S08]

**红队验证。** 用无真实密钥的假敏感文件及假网络端点测试：恶意 README 诱导读取文件、Issue 诱导修改 workflow、工具返回诱导执行 Shell、PR 诱导 exfiltrate。记录操作是否实际被 OS/tool policy 阻止，而不仅是 Agent 最终说了“拒绝”。

**验收。** 未授权读写与外联在执行层被拦截；风险目录触发审批；所有高权限操作有身份、参数、批准人与可核验记录。**剩余风险：** 社工、人为误批、依赖投毒、容器逃逸等仍需防御纵深与事故响应。

### I04｜“假成功”与结果不可核验：证据账本 + 外部状态核对

**根因。** 模型把“已尝试调用”“工具成功返回”“PR 已创建”“PR 已合并”“部署已生效”混为同一种成功，外部异步作业失败又未回查。

**现成方案。** GitHub PR/Checks/Deployments API、GitHub Actions Run、制品哈希、环境健康检查、受控审计日志。保护分支与 Rulesets 支持必需审查和状态检查；Artifact Attestations 可以绑定工作流、Commit 与制品来源，但必须实际验证，且不证明制品安全。[S06][S11]

**实施步骤。** ① 定义状态 `PATCHED→CI_RUNNING→CI_PASSED→PR_OPEN→MERGE_ELIGIBLE→MERGED→DEPLOYED→BUSINESS_VERIFIED`；② 所有状态迁移都有 `source_provider/source_id/observed_at/subject_sha`；③ 在状态读写中使用单调迁移与幂等键，处理 webhook 重投；④ 异步 CI/merge/deploy 用轮询或 webhook 最终一致性核对；⑤ 状态不明时返回 `UNKNOWN/NOT_VERIFIED`，而非成功。

**必须区别：** PR 开启不是合并；GitHub Workflow 成功不代表线上健康；构建制品存在不等于用户可访问；部署完成也不等于业务流无异常。

**验收。** 模拟 PR 保持 Open、CI 失败、Deploy 超时、Artifact 缺失，报告不能写完成；证据账本可反查每次状态变更。指标 `False Completion Rate` 和 `Evidence Coverage`。

### I05｜大型仓库上下文不足：分层检索、符号图和版本化知识

**根因。** 全仓库塞入上下文既昂贵又失焦；纯向量检索对符号名、调用链、配置/测试位置不稳定；文档与当前 Commit 可能不匹配。

**现有方案比较。**

| 方案 | 代表工具 | 最适用 | 局限 |
|---|---|---|---|
| 精确词法检索 | ripgrep / GitHub Code Search / Zoekt | 错误消息、函数名、配置键 | 找不到语义同义表达 |
| AST/Symbol Repo Map | tree-sitter、Aider Repo Map、LSP | 函数、定义、引用、接口 | 跨语言动态调用仍难 |
| 依赖图/调用图 | LSP、SCIP/LSIF、构建工具依赖图 | 大规模跨文件改动 | 索引构建和增量更新 |
| 文档检索 | 混合搜索/BM25+向量 | ADR、设计说明、API 解释 | 易读到过期说明 |

Aider 的 Repo Map 使用符号提取与图相关性在 Token 预算内筛选重要定义；Zoekt 提供面向代码库的自托管高性能检索参考。[S12][S13]

**推荐实现。** ① 对每个 `base_sha` 构建文件清单、语言索引和关键依赖；② 先搜索 `rg` 精确关键词，再按符号引用扩展，最后按需读文件主体；③ 上下文附 `path/line/commit/why_relevant`；④ 引用的外部 API 文档记录版本和检索日期；⑤ 限制上下文预算，优先维护“任务涉及的调用链、测试与变更点”；⑥ 对 Agent 的“某函数不存在”“某文件唯一实现”等断言要求代码索引证据。

**验证。** 用已知历史 Bug 标注 gold files，测 Top-k File Recall、误召回率、检索成本，并测试不同仓库规模。**反模式：** 把所有历史聊天记忆无选择地注入下一轮。

### I06｜工具调用/CLI/MCP 配置脆弱：规范化 Tool Gateway

**根因。** 模型会误用工具；不同 Agent 的权限配置语法并不兼容；MCP 工具版本、请求字段、返回结构可能变化；瞬时 429 与不可恢复 403 被错误重试。

**三类现有方案。**

- **Schema-first：** JSON Schema/Pydantic 验证调用参数与返回值，注册工具版本与 schema 哈希，拒绝未知字段；对不可信 `description/annotations` 不直接授予权限。[S03]
- **统一错误语义：** `VALIDATION_ERROR`、`PERMISSION_DENIED`、`NOT_FOUND`、`RATE_LIMITED`、`TRANSIENT_NETWORK`、`TIMEOUT`、`EXECUTION_FAILED`；每类有固定 `retryable`、重试上限与日志。
- **专用 Adapter：** 为 Codex、Claude、OpenCode、Pi 分别生成配置并在启动前执行 dry-run，不共享未经转换的配置文件。Claude Code 的 JSON 权限规则与某些其他 Agent 的 YAML 权限语法不能机械互换。[S08]

**执行策略。** 对读取型工具可以有限重试与指数退避；对 Git Push、PR 创建、包发布、支付等带副作用工具必须由幂等键或外部状态查询保护，不能盲目重复。对危险 Shell 使用可审计命令模板和最小可执行权限。任何修复操作都要记录 tool request/response、退出码、stderr、实际写入文件列表。

**验收。** 注入 schema 错误、404、429、网络抖动和重复 webhook；确认不会无限重试或重复写入。指标 Tool Schema Pass、Retry Amplification、Side-effect Duplicate Count。

### I07｜构建依赖与环境漂移：不可变基线 + Lock + Baseline CI

**根因。** “我的机器可用”依赖未记录的 SDK、动态下载脚本、包镜像、OS、CPU 架构或缓存状态。Agent 可能为了通过测试随手升级依赖，掩盖真正错误。

**现成方案。** Devcontainer/Dockerfile、Nix、uv / pip-tools、npm ci / pnpm lockfile、Cargo.lock、Go modules、Testcontainers。Python `uv run --locked` 可在锁文件过时时直接报错，而不是默默重写锁文件。[S14]

**落地。** ① 保存 `os/arch/toolchain/runtime/dependency_lock_hash/base_image_digest`；② 从指定 `base_sha` 启动干净容器运行 baseline；③ Agent 只能在隔离分支中修改依赖，锁文件变化须单独审查；④ 为外部服务区分 Mock/真实集成测试；⑤ 每个候选 Patch 在相同锁定环境复测；⑥ 修复故障时先证明错误是“基础环境已有”还是“变更引入”。

**选型边界。** Docker 容器提高复现性但未保证完全确定性；Nix 更强调构建依赖可再现，但上手成本较高；Testcontainers 更贴近真实数据库，但启动慢且要求 Docker 环境。

**验收。** 同 SHA 在干净 Worker 上能够按文档复现，故障报告准确区分 `BASELINE_FAIL` 与 `REGRESSION_FAIL`，并跟踪冷启动成本。

### I08｜长任务失忆、漂移与修复循环：持久化 DAG / Checkpoints / 有界预算

**根因。** 长任务涉及多次工具调用和外部副作用；上下文压缩丢失约束，失败后盲目重试；进程崩溃时内存状态消失。

**工具对照。**

| 工具类别 | 现有实现 | 优势 | 重要限制 |
|---|---|---|---|
| Agent 图状态 | LangGraph Checkpointers | 图节点状态持久化、恢复与人工介入 | 需外部副作用幂等；本地内存 Saver 不抗重启 |
| 通用持久工作流 | Temporal | 事件历史、Worker 重启恢复、Activity 重试/心跳 | 运维和确定性工作流设计复杂 |
| Git 快照 | Git Worktree、Commit/Tags | 代码级可回滚、易审查 | 不保存外部 API 副作用与模型内部状态 |

LangGraph 文档列明 Postgres Saver 可用于持久检查点；Temporal 明确提醒 Activity 即便最终只记录一次完成，执行本身可能重复，因此写操作必须幂等。[S15][S16]

**推荐阶段机制。** `PLAN → IMPLEMENT → TEST → REVIEW → PR` 每阶段有输入摘要、输出 hash、环境摘要、风险和支出；超过 `max_fix_attempts`、重复相同错误三次或连续两轮无有效进展就进入 `BLOCKED`。恢复时先验证 Worktree SHA、任务租约和外部副作用，不能只重放模型消息。

**验收。** 在运行到 30%、60%、90% 处强制杀掉 Worker，重启后不丢任务、不重复 PR、不把部分执行标记完成；记录 Resume Success 和 Duplicate Side Effects。

### I09｜代码膨胀与 Review 负担：增量质量门禁与差异优先审查

**根因。** Agent 容易使用最直接的补丁，而不是现有抽象；大型 Diff 超过人类有效审查容量；功能测试无法发现维护性退化。

**方案栈。** `git diff --check` + Ruff/ESLint/tsc + CodeQL/Semgrep + 重复代码检测/复杂度检查 + CODEOWNERS + 独立 Reviewer。GitHub CodeQL 可配置为 PR 和受保护分支的扫描，具体支持范围取决于代码语言、仓库类型与服务权限。[S17]

**执行方式。** ① 评估变更的 SLOC、文件数和高风险目录，不依赖统一硬阈值；② 对过大变更要求拆为接口层、实现层、测试层的可审查提交；③ 分别输出 `correctness/security/maintainability` 审查结果；④ 与基线比较“新增问题”，避免把遗留技术债全部归咎于本次 Agent；⑤ 对 LLM Reviewer 的结论要求代码位置和具体复现，不接受笼统评分。

**权衡。** 过严的复杂度阈值会打断合理重构；静态分析存在误报和漏报；人工审查仍是高风险更改的重要控制。

**验收。** 新增高严重级别安全告警为零或已审批处置；Review 变更请求可归因；统计每成功任务的 Review 分钟而不是每 PR 的评论数。

### I10｜状态、数据库事务与并发问题：性质测试 + 真实服务集成 + 线上约束

**根因。** UI 级别成功提示可能与真实数据持久化脱节；竞态、重复请求、隔离级别、延迟消息、灰度部署版本混杂，普通单元测试不会覆盖。

**可用做法。** 对 CRUD 功能，用 Playwright 断言 `提交→API 返回→数据库状态→页面刷新后状态` 一致；对异步任务，用可观察 Job ID + 后端最终状态；对金额/库存，用数据库唯一约束与事务 + 基于性质的测试；对迁移执行 expand-contract 分阶段方案和兼容性窗口。Playwright 的异步断言可降低 UI 等待相关误报，但不能证明数据库事务正确。[S09]

**高价值场景。** 测试两个并发退款请求、重复 webhook、事务中途异常、消息乱序、网络超时后重试、应用重启之后重复投递；验证唯一索引、锁与幂等键在服务端真正生效。

**失败条件。** 仅检查 Toast 文案、仅 Mock 数据库、只跑单线程正常路径都不能构成生产级验收。**指标：** UI-DB State Mismatch、Idempotency Failure、Invariant Violation、Migration Rollback Readiness。

### I11｜多 Agent 并发写入冲突：独立 Worktree + 依赖 DAG + 集成门禁

**根因。** 多个 Coder 共享同一个工作目录或使用同一接口假设，会造成文件覆盖、分支漂移、重复劳动，最终把并行节省的时间消耗在集成中。

**推荐路径。** ① Planner 将任务分解为独立模块与输入输出契约；② 每个任务从同一已知 base commit 建立独立 Git Worktree 和执行容器；③ 对共享 schema、数据库迁移、公共接口设模块 Owner 和依赖排序；④ 先合并基础契约，再执行可并行子任务；⑤ 合并前重算冲突、rebase 或使用 Merge Queue 在合成提交上重跑 CI；⑥ 限制并发数量以控制 Review WIP。

**比较。** 独立 Worktree 是必要的文件系统隔离但不提供安全沙箱；Merge Queue 可减少 busy branch 中的基线竞态，但不消除业务层冲突。GitHub Merge Queue 要求 `merge_group` 事件触发必需检查，且可用性受到仓库/套餐条件影响。[S18]

**验收。** 多 Agent 同时改动模拟共享接口时，系统可以阻塞或排序而不会覆盖；合并后的真实 merge-group commit 通过测试。指标冲突率、返工、综合交付时间。

### I12｜CI / PR / 发布最后一公里：保护分支 + Merge Queue + 制品证明 + 灰度

**问题。** Agent 的补丁在 `head_sha` 上测过，却合并了另一代码状态；CI Checks 由非可信来源伪造；部署任务成功返回但应用版本未更新。

**现成控制。** GitHub Rulesets/Branch Protection、required checks 与指定 Check 来源、Merge Queue、Environments 与审批、OIDC 短期凭证、Artifact Attestations（构建来源）、部署健康检查与业务指标门禁。[S06][S11][S18]

**实施顺序。** ① 分别定义 `PR_CREATOR`、`MERGER`、`DEPLOYER` 权限；② CI 必需状态来自受信任 App，不允许任意写入来源冒名顶替；③ 如果使用 Merge Queue，检查实际 `merge_group` 合成代码而不只 PR head；④ 发布制品保存 SHA256、镜像 digest 与构建证明；⑤ 灰度时追踪健康、错误率、关键业务不变量；⑥ 实现停更/回滚机制并验证真正恢复到目标版本。

**边界。** 制品签名证明的是来源，不代表无漏洞；单次健康检查成功不保证一段时间后的行为正确；回滚数据库迁移可能不可逆。

**验收。** 通过伪造或过期 CI 状态、强制失败部署、变更后未复测等故障注入检查所有门禁；任务只有在部署版本与期望 digest 一致且业务检测通过后才进入 `BUSINESS_VERIFIED`。

### I13｜成本、速率、审查队列：成本归因 + 路由 + 重试预算

**核心误区。** 价格低的模型并不必然拥有低交付成本；多个 Agent 并发可能成倍增加搜索、测试和 Reviewer 的重复劳动。

**现有方案。** 模型/API Gateway（如 LiteLLM Router）可提供多模型路由、失败切换和重试控制；需要特别区分 Router 的重试与底层 SDK 重试，避免“重试倍增”。[S19] 预算与调度应由自己的 Orchestrator 强制执行，而非仅依赖模型提示。

**可落地策略。** ① 将任务按复杂度/风险/环境负担路由，小修复先由低成本模型尝试；② 限制 `model_calls/tool_calls/input_tokens/wall_clock/parallelism/max_fix_attempts`；③ 用缓存减少重复代码索引与不变文档读取；④ 失败分类，已知配置错误直接阻塞而不是重复调用强模型；⑤ 对 Review 队列设置 WIP 限额；⑥ A/B 统计“成功验收任务的总费用”，包含模型、沙箱、CI、人工审核、返工和生产事故处理。

**谨慎点。** 为追求低 Token 把上下文删到无法解决问题，反而增加误改；缓存必须绑定 Git SHA 或文档版本；预算被耗尽不是自动成功，而是可解释的 `BUDGET_EXCEEDED`。

**验收。** 以相同任务集统计每有效验收任务总成本和 P50/P95 交付时延，报告成功率与风险，不只比较 API 调用费用。

### I14｜Benchmark 失真：私有真实任务 + 双向验收 + 滚动评估

**根因。** 公开基准可能与训练数据重叠、测试过窄、要求未写进任务说明，或被 Agent 通过依赖缓存等方式绕过；高 pass@1 不能代表真实研发效率。[R04][R05]

**现有参考。** SWE-Bench Pro V2 的任务清洗与双向测试、干净镜像复评；公司内部的真实历史任务回放；任务对照实验；独立代码 Reviewer 和人工抽样。[S01]

**具体设计。** ① 将历史真实 Issue 连同 `base_sha`、原始需求、参考补丁、回归测试打包为评估夹具；② 用 `reference patch passes / empty patch fails` 做数据清洗；③ 拦截外网查找修复 Commit，清理任务镜像中的答案泄露；④ 同一任务用多模型重复测试，记录方差与置信区间；⑤ 对通过样本抽查隐藏业务缺陷；⑥ 定期引入最近的真实 Bug 作为滚动集；⑦ 单独报告“工具设置失败、模型找错文件、验证器问题”。

**验收。** 任务数据集有版本和可重放脚本；每条失败可归因；不以基准结果取代生产流量观察。

### I15｜知识库、AGENTS.md 与 Skills 漂移：Docs-as-code + 版本/适用域治理

**根因。** 长期积累的规则发生冲突：README 写旧命令、AGENTS.md 含过期结构、Skill 引用失效脚本、MCP schema 更新后适配器失效。Agent 越听话，错误规则越容易被稳定执行。

**方案。** 文档使用 Git 版本管理；为 `AGENTS.md` 规定最小内容（构建入口、测试入口、边界、代码规范），详细方法放入 `skills/**/SKILL.md`，深度知识放在 `references/`；每条重要规范标注 `owner/last_verified/compatibility`；CI 校验路径、命令和链接；定期从真实脚本反推文档是否有效。Claude Code 的设置文档还强调不同设置文件的优先级以及配置无效时可能被跳过的情况，说明必须做配置 smoke test。[S08]

**实践细节。** 不要把 GitHub 外部 README、Agent Tool Description 直接提升为管理策略；对 Skills 引用的脚本使用固定提交和本地签名/哈希；新增框架时给专用 Adapter 增加配置校验用例。

**验收。** `docs-check` 能验证文档中给定的安装/测试命令；过期引用自动提示；关键 Skill 在指定环境运行 smoke test；统计 `Stale Knowledge Incidents`。

### I16｜缺少可观测性与失败复盘：OpenTelemetry + Evidence Ledger + Failure Taxonomy

**根因。** 常见 Agent 执行记录只有最终聊天文本，缺少工具参数、Git 变更、模型调用、验证器版本和真实系统状态；不可重放即不可科学优化。

**成熟方案。** OpenTelemetry GenAI 语义约定提供模型调用、Token、工具执行和 Trace 相关字段；需注意其部分语义仍处于 Development 稳定级别，采集 Prompt/工具输出可能包含敏感信息。[S20] 可在此基础上使用 Jaeger、Tempo、Phoenix、Langfuse 等做 Trace 可视化，并另建业务级 Evidence Ledger。

**事件最小字段。** `run_id/task_id/attempt_id/step_id/parent_span_id/model/agent/tool/tool_schema_hash/allowed/exit_code/error_code/retryable/input_digest/output_digest/base_sha/head_sha/tested_sha/ci_run_id/cost/status/timestamps`。

**实施步骤。** ① Orchestrator、模型网关、Tool Gateway、沙箱、CI 统一关联 Trace ID；② 采集结构化指标，不默认保存完整 Prompt、密钥或原始代码；③ 记录不可变失败分类与“首次触发错误”的证据；④ 构建可回放但默认脱敏的 Trace 视图；⑤ 定期把失败案例转化为回归任务与故障注入测试；⑥ `SOURCE_UNAVAILABLE` 和 `UNKNOWN` 不得被统计为通过。

**验收。** 对随机抽取的失败任务可以在几分钟内定位首次失败的工具调用或测试证据；所有最终状态均可追溯到外部系统；记录 `Trace Coverage` 与 `Time to Root Cause`。

### 4A.17 横向技术选型表：没有一种工具能解决全部问题

| 目标 | 低成本起步 | 可规模化方案 | 需要特别警惕 |
|---|---|---|---|
| 需求入口 | Issue Form + JSON Schema | 风险引擎 + 任务契约数据库 | 不能完全自动消解含糊需求 |
| 代码理解 | rg + tree-sitter + Repo Map | Zoekt/符号索引/依赖图 | 索引版本必须与 Commit 对齐 |
| Agent Runtime | 单 Agent + Worktree | Worker 池 + 容器/VM + Adapter | Worktree 不等于安全沙箱 |
| 任务编排 | SQLite/PostgreSQL 状态机 | Temporal / LangGraph + 事件账本 | 外部写操作仍需幂等 |
| 测试验证 | pytest/Jest + CI | 性质/变异/集成/E2E + 独立干净复评 | 测试通过不代表业务完整 |
| 安全 | OS 权限 + Repo Protect | Tool Gateway + OPA/策略 + 短期令牌 | Prompt 防护不是强制执行 |
| PR/发布 | GitHub branch rules + checks | Merge Queue + Env Gate + Attestations | 检查真实合成 Commit |
| 观测与评测 | 结构化日志 + JSONL | OTel + Trace UI + Eval Dataset | 采集需脱敏且可审计 |
| 成本管理 | 每任务预算 + 串行限制 | Model Gateway + 路由 + WIP | 优化“有效交付”非单次 Token |

**选型原则：** 若当前团队只有 1—5 个仓库、低并发任务，优先用 GitHub Actions、PostgreSQL、独立 Worker 和沙箱搭建最小闭环；当任务经常跨多小时、涉及外部写入且需要灾难恢复时，再引入 Temporal；如果核心痛点是复杂 Agent Graph 与人机交互，评估 LangGraph；如果两者并存，可分层组合，但需要避免重复持久化与重复重试。


---

## 5. 三个必须认真分析的故障案例

### 案例 A：生成代码“跑通”但业务没有完成

**观察**：DAPLab 2026 对多种应用的研究记录了“按钮成功提示但数据库/状态没有持久化”等静默失败；多轮修改还可能破坏已完成的功能。[R03][R13]

**根因链**：界面可视化效果被过度当作验收代理 → 缺少跨组件状态检查 → 单元测试没有真实数据断言 → Agent 声称完成。

**控制方案**：每条业务旅程生成 UI 操作 + 服务请求 + 数据库持久化三段证据；错误路径和刷新后状态恢复作为必测项。

### 案例 B：SWE Benchmark 验证器也会犯错

**观察**：OpenAI 2026-07 的 SWE-bench Pro 审计发现大量任务描述与隐藏测试不一致或不充分；Scale 的 2026-09 V2 进一步清洗任务、改进依赖和二次隔离复评。[R04][R05]

**根因链**：测试被当作绝对真理 → 对正确提交产生假阴性，或因低覆盖对错误补丁产生假阳性 → 模型训练/工程决策被错误分数误导。

**控制方案**：保持参考补丁通过、空补丁失败的双向校验；接受实现差异；记录测试变更版本；对边缘任务安排专家审查。**评测平台也是被测的软件**。

### 案例 C：不可信 GitHub 内容跨越权限边界

**观察**：微软 2026-06 研究指出 GitHub Action 中不可信 Issue/PR 内容与具有机密读取能力的 Agent 相组合，会形成越权风险；特定 Read 路径能够读取 `/proc` 敏感环境信息。[R09]

**根因链**：外部用户输入被模型解释为操作指令 → Agent 的文件读取权限广于业务需要 → Runner 存在高价值环境变量 → 安全控制未覆盖所有工具入口。

**控制方案**：Issue Triage 与代码写入拆为不同低权限作业；不可信任务不暴露密钥；敏感文件和出站联网通过工具与 OS 级别限制；只将经过授权的结构化请求交给高权限工作流。

---

## 6. 推荐的生产架构：以验证为中心

```mermaid
flowchart TB
    A[User / Issue / CI Failure] --> B[Task Intake + Risk Classification]
    B --> C[Task Contract: acceptance + scope + permissions]
    C --> D[Orchestrator: state + budget + retries]
    D --> E[Context Engine: symbols + dependencies + documents]
    D --> F[Coder Agent in isolated worktree/container]
    E --> F
    F --> G[Tool Gateway: schema + policy + audit]
    G --> H[Repo / Shell / LSP / Browser / APIs]
    F --> I[Independent Verification]
    I --> I1[Build + unit + integration + E2E]
    I --> I2[Security + property + regression]
    I --> I3[Clean-room re-grade + provenance]
    I --> J{Policies satisfied?}
    J -- No --> K[Bounded fix or Blocked]
    K --> D
    J -- Yes --> L[Review + protected PR]
    L --> M[CI / merge queue]
    M --> N[Deploy + health + business invariant]
    N --> O[Evidence ledger + incident feedback]
    O --> C
```

**关键设计**：
- LLM 负责提出实现动作，不负责定义自己的成功判据。
- 工具网关负责校验 schema、路径、权限和审计；OS/容器负责物理隔离。
- 独立验证器对真实提交进行验证；审核结果不能依赖一段自然语言自评。
- Orchestrator 仅在外部系统确认后转换状态，所有任务都可重放、追责、限额。

### 6.1 任务状态机

`QUEUED → TRIAGED → PLANNED → RUNNING → VALIDATING → REVIEWING → PR_OPEN → MERGE_ELIGIBLE → MERGED → DEPLOYING → VERIFIED`

额外终态：`BLOCKED_SPEC` / `BLOCKED_PERMISSION` / `FAILED_ENV` / `FAILED_TEST` / `FAILED_SECURITY` / `CANCELLED` / `ROLLED_BACK`。任务状态不能只用布尔 `success` 表示。

### 6.2 可操作的任务契约

```yaml
task_id: ISS-2026-001
repository: owner/repo
base_ref: main
risk_tier: medium
objective: "修复重复退款导致的金额不变量破坏"
non_goals:
  - "不改动结算服务的公开 API"
allowed_paths:
  - "src/refunds/**"
  - "tests/refunds/**"
protected_paths:
  - ".github/workflows/**"
  - "infra/**"
acceptance:
  - id: A1
    type: business_invariant
    rule: "sum(refunds) <= paid_amount"
  - id: A2
    type: integration
    rule: "并发与幂等测试通过"
  - id: A3
    type: regression
    rule: "既有测试不回归"
limits:
  max_fix_attempts: 3
  max_tool_calls: 100
  network: restricted
merge_policy:
  require_independent_verification: true
  require_review: true
  auto_merge: false
```

### 6.3 可机器核验的交付证据

```json
{
  "task_id": "ISS-2026-001",
  "head_sha": "<40-char-commit-sha>",
  "environment_digest": "sha256:<digest>",
  "verification": {
    "test_run_id": "<run-id>",
    "tested_sha": "<same-commit-sha>",
    "result": "passed",
    "source": "ci-provider"
  },
  "pull_request": {
    "url": "https://github.com/owner/repo/pull/123",
    "state": "open",
    "source": "github-api"
  },
  "deployment": {
    "state": "not_deployed",
    "source": null
  },
  "final_status": "PR_OPEN_NOT_MERGED"
}
```

上面是字段约定示例，不是真实项目执行结果。关键是明确定义：**PR Open ≠ Merged；CI Passed ≠ Deployed；Deployed ≠ Business Verified**。

## 6A. 从解决方案到可运行系统：生产实施配方（新增）

### 6A.1 统一生产链与责任分离

```mermaid
flowchart TD
    U[Issue / Bug / Product Requirement] --> T[Contract & Risk Policy]
    T --> P[Planner and Context Retrieval]
    P --> W[Ephemeral Sandbox / Worktree]
    W --> G[Tool Gateway / Model Router]
    G --> A[Coder Agent]
    A --> V[Independent Tests / Clean Environment]
    V -->|fail and under budget| A
    V -->|pass| Q[Static / Security / Human or Independent Review]
    Q -->|approved| PR[Protected Pull Request]
    PR --> MQ[Merge Queue + Required Checks]
    MQ --> DEP[Staged Deployment + Attestation]
    DEP --> BIZ[Business Verification]
    BIZ --> EV[Evidence Ledger / Trace / Evaluation]
```

**职责拆分：** 用户/产品 Owner 确定需求和高风险例外；Planner 只产出计划；Coder 只能在隔离区写补丁；Verifier 只消费已锁定的候选 Commit；Review 决定是否符合质量标准；Git Provider/CI/部署服务提供终态事实；Orchestrator 只做有证据的状态转换。这样避免“自己出题、自己改卷、自己宣布过关”。

### 6A.2 工具调用 Policy Gate：平台无关的决策接口

下面是**架构伪代码**，不是可直接部署的生产安全模块：

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Action:
    run_id: str
    actor: str
    operation: str
    target: str
    args: dict
    approval_id: str | None


def authorize(action: Action, identity, policy, approvals):
    # 1. Never trust the model or tool description for authority.
    if not policy.actor_may_call(identity, action.operation):
        return "DENY"
    # 2. Canonicalize paths/URLs before checking exact scopes.
    if not policy.target_is_allowed(action.operation, action.target):
        return "DENY"
    # 3. Bind approval to exact operation, target, and arguments.
    if policy.is_high_risk(action):
        return "ALLOW" if approvals.matches(action) else "REQUIRE_APPROVAL"
    return "ALLOW"
```

**补齐生产控制：** 路径规范化防目录穿越/符号链接逃逸、具体参数的 schema 校验、MCP 工具身份绑定、短期令牌、文件系统挂载隔离、网络 egress allowlist、执行超时、最大输出体积、审计日志、失败默认拒绝。即使本层产生错误，OS/容器策略仍要独立限制实际可访问资源。[S02][S03][S05]

### 6A.3 可直接移植的验证任务样例

下方示例用于 **Python 仓库** 的低权限 PR 测试；具体包名、版本和测试命令应按目标项目适配。若使用 GitHub Merge Queue，要增加 `merge_group` 触发，详见 GitHub 官方文档。[S18]

```yaml
name: Agent PR verification
on:
  pull_request:
  merge_group:
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4 # 生产应 pin 到审计过的完整 commit SHA
      - uses: astral-sh/setup-uv@v6 # 生产应 pin 到审计过的完整 commit SHA
      - name: Verify lockfile and install
        run: uv sync --locked
      - name: Static checks
        run: uv run ruff check .
      - name: Tests
        run: uv run pytest -q
```

**必要说明：** 此例本身不会自动检查业务验收、代码扫描、依赖安全、构建制品来源或生产部署；这些需要在目标仓库中额外设置为必需检查。对于外部 PR，执行不可信代码的 Job 不得接触长期生产密钥，也不应将其与可写生产仓库的高权限流程拼接。[S07]

### 6A.4 将不变量从 Prompt 变成可执行测试

以下演示对一个**纯函数**的通用性质测试：

```python
from hypothesis import given, strategies as st

# Implementation to test: apply_refund(paid, refunded, amount) -> new_refunded
@given(
    paid=st.integers(min_value=0, max_value=1_000_000),
    refunded=st.integers(min_value=0, max_value=1_000_000),
    amount=st.integers(min_value=0, max_value=1_000_000),
)
def test_refund_never_exceeds_payment(paid, refunded, amount):
    if refunded > paid or amount > paid - refunded:
        return  # Precondition: only test permitted refunds here
    result = apply_refund(paid, refunded, amount)
    assert refunded <= result <= paid
    assert result == refunded + amount
```

**重要局限：** 这是对假设存在的 `apply_refund` 函数的示意，未提供其实现，也未测试数据库并发更新、重复请求、事务回滚和实际支付行为。生产版本应再增加拒绝非法退款金额的负面测试和两个并发请求的真实数据库集成测试。[S10]

### 6A.5 交付证据的不变量

由平台验证以下逻辑关系，而不是交给模型判断：

```text
PR_OPEN does not imply MERGED
CI_PASSED does not imply DEPLOYED
DEPLOYED does not imply BUSINESS_VERIFIED

For PR-head verification:
  reported_ci_sha == expected_pr_head_sha

For merge queue verification:
  reported_ci_sha == merge_group_candidate_sha

For release artifact:
  deployed_artifact_digest == verified_artifact_digest
```

GitHub Merge Queue 的检查对象可能是合成提交而不是单独 PR Head；因此直接要求 `tested_sha == PR Head SHA` 只适用于不使用 Merge Queue 的单分支验证流程。[S18]

### 6A.6 失败注入与恢复测试矩阵

| 注入故障 | 应观察的系统行为 | 合格条件 |
|---|---|---|
| Agent 修改后 CI 失败 | 停留 `FAILED_TEST` 或有界重修 | 不创建虚假成功报告 |
| 修改测试代码规避验收 | 验证器保护/复评检测 | 不自动合并 |
| 无效 MCP Tool Schema | 入口校验拒绝 | 不进入模型自由纠错死循环 |
| 429/5xx 瞬时错误 | 受控退避和预算消耗 | 无重试风暴 |
| 403/无效参数 | 不重试，返回权限/配置问题 | 有明确错误码 |
| 执行中断或 Worker 宕机 | 持久任务可恢复 | 没有重复创建 PR/发布 |
| 恶意 README 诱导读取密钥 | 沙箱/工具网关拒绝 | 实际文件读取失败 |
| PR Head 更新后旧 CI 通过 | 旧验证状态失效 | 对新候选重测 |
| Merge Queue 合并冲突 | 被移除队列或阻塞 | 不绕过 required checks |
| 发布成功但健康检查失败 | 停更/回滚/人工处理 | 不写 `BUSINESS_VERIFIED` |
| 全部测试通过但业务数据未落库 | E2E/DB 对账失败 | 不予业务验收 |
| Trace 采集服务不可用 | 保留本地结构化事件/明确缺失 | 不将证据缺失误作成功 |

### 6A.7 优先级、人员与交付标准

| 交付周期 | 建设项 | Owner 角色 | 可客观判断的完成定义 |
|---|---|---|---|
| P0：第 1—2 周 | Task Schema + 禁止越权操作 | Tech Lead / Security | 不合格任务被阻塞；拒绝测试通过 |
| P0：第 2—4 周 | 独立验证 / Commit 证据 / 外部终态 | QA / DevEx | SHA 错配与假成功测试全部阻断 |
| P1：第 5—6 周 | Repo Map + Baseline Env | Platform / Repo Owner | 选定历史 Bug 的文件召回与复现率可记录 |
| P1：第 7—8 周 | State Checkpoints + Trace + Review Gate | Platform / SRE | 杀 Worker 后恢复、无重复副作用 |
| P2：第 9—12 周 | 多 Agent 并发、成本路由、回归评测 | Platform / Engineering | 配对实验显示收益且风险门禁不退化 |

**资源估算说明：** 上表是工作包相对顺序，不是任何团队的承诺工期。人员数量、仓库规模、CI 时长、安全要求、内部合规会显著影响交付周期。

### 6A.8 任务分层与自动合并策略

| 风险层级 | 示例 | 允许的自动化程度 |
|---|---|---|
| R0 只读 | 分析错误日志、汇总代码位置 | 可自动执行；限制资料访问 |
| R1 低风险 | 文档链接、明确的小范围非功能修复 | 自动 Patch/PR；合并仍受仓库规则约束 |
| R2 中风险 | 公开 API、依赖升级、一般服务 Bug | 独立验证和 Review 后合并 |
| R3 高风险 | 鉴权、支付、密钥、CI、数据库迁移、发布配置 | 高强度验证，明确的授权审批；默认禁止自动合并 |

适用风险等级必须由业务和安全负责人确认；不建议仅依据“改动行数少”认定 R1，少量代码也可能造成高影响后果。


---

## 7. P0/P1/P2 解决方案优先级

### P0｜先让系统不会错误宣称交付成功，也不会越权（0—30 天）

| 交付包 | 最小实现 | 验收方法 |
|---|---|---|
| P0-1 任务契约 | Issue Schema、风险评级、验收、不变量、禁止操作范围 | Schema 校验、缺字段阻塞 |
| P0-2 隔离与权限 | 每任务 Worktree/Container、最小权限 Token、无生产密钥 PR 环境 | Prompt Injection 红队用例被拦截 |
| P0-3 证据化验证 | CI 与 Head SHA 绑定、独立测试、干净环境复评 | 更改 Commit 后旧证明自动失效 |
| P0-4 状态真相 | 外部 GitHub/CI/Deploy 返回驱动状态机 | 未合并 PR 不会标记 Merged |
| P0-5 失败可见 | 标准错误分类、失败归因、Trace 保存 | 模拟失败可重现、可定位 |

### P1｜建立长期任务与工程质量能力（30—60 天）

| 交付包 | 最小实现 | 验收方法 |
|---|---|---|
| P1-1 Repo Understanding | `rg + LSP + AST + 依赖索引` | 相关文件检索召回率测试 |
| P1-2 可复现环境 | 镜像摘要、锁文件、baseline 测试 | 相同 SHA 重跑一致性达标 |
| P1-3 修复预算与恢复 | Checkpoint、执行日志、预算上限、重入幂等 | 中断后可恢复，预算耗尽不无限重试 |
| P1-4 Review 与债务门禁 | Diff/重复度/复杂度增量、风险目录审查 | 大 Diff 被拆分或升级审批 |
| P1-5 Eval Harness | 私有真实任务 + 两种以上 Agent | 同预算、同环境可比较 |

### P2｜多 Agent 与规模化生产（60—90 天及以后）

| 交付包 | 最小实现 | 验收方法 |
|---|---|---|
| P2-1 多 Agent 协同 | 按模块隔离并行、接口契约、依赖 DAG | 不发生共享工作区污染 |
| P2-2 成本路由 | 简单任务小模型、复杂任务强推理、缓存 | 降低有效验收任务成本 |
| P2-3 低风险自动合并 | 白名单仓库 + Policy Gate + 必需 Check | 无人工干预的改动全部可追溯 |
| P2-4 生产反馈闭环 | 灰度、业务不变量、回滚、事故复盘 | 漏测形成回归任务和验证样例 |

## 8. 测量体系：不要再以“写了多少代码”作为 KPI

| 指标 | 公式/定义 | 为什么重要 |
|---|---|---|
| Verified Resolution Rate | 独立验收成功任务 / 所有尝试任务 | 衡量真正完成 |
| False Completion Rate | 自报成功但外部未验证任务 / 自报成功任务 | 衡量失真 |
| Escaped Defect Rate | 交付后实际缺陷 / 有效交付任务 | 衡量质量尾部风险 |
| Effective Lead Time | 从需求被接受至独立验收的用时 | 衡量交付效率 |
| Cost per Accepted Task | 模型+计算+人工审核+返工成本 / 验收成功任务 | 衡量总体经济性 |
| Review Burden | 人工审查分钟 / 已验收任务 | 防止瓶颈后移 |
| Tool Error Rate | 失败工具调用 / 总工具调用 | 衡量执行层可靠性 |
| Recoverable Run Rate | 中断后可正确恢复的任务 / 中断任务 | 衡量长任务韧性 |
| Security Policy Violation Rate | 被检测到的违规行为 / 执行任务 | 衡量权限治理 |
| Trace Completeness | 证据齐全任务 / 所有任务 | 衡量审计能力 |

**测量注意**：必须分层报告语言、仓库规模、任务风险、Agent 类型、是否自动合并、是否有人审查。不跨样本直接比较不同团队的百分比。

## 9. 一套可执行的 30 天评测实验

**实验目标**：不是选“最聪明模型”，而是识别公司/仓库中影响交付成功率的 P0-P1 根因。

1. **任务集**：至少选择 30—50 个真实历史任务，覆盖 Bug、功能、重构、依赖、CI、数据库、安全；为各任务保存基线 Commit 和规范验收。
2. **配对设计**：至少 2 个 Agent/模型组合，在相同容器、权限、输入、工具预算下执行；记录人工干预。
3. **独立评估**：运行任务原有测试之外的验收、隐藏边界/性质测试、质量扫描、权限红队用例，评估 Head SHA。
4. **事件归因**：每次失败只能有一个主因但可有多个次因；必须分清 `MODEL/CONTEXT/TOOL/ENV/TEST_ORACLE/POLICY/CI/DEPLOY`。
5. **结果呈现**：按任务难度、仓库、Agent 输出成功率、平均成本、P95 时长、人工审查时长和前三大根因。
6. **复核与重复**：对统计不确定的任务进行重跑；随机抽取通过任务做人工审计，估计假通过率。

**可交付数据集字段**：`task_id, repository, base_sha, agent, model_version, attempt_id, risk_tier, outcome, primary_failure, secondary_failures, head_sha, test_sha, verification_source, tool_errors, retries, tokens, cost, review_minutes, delivery_state, trace_uri`。

## 10. 成熟度自评清单

以下问题若回答“否”，应优先建立相应 P0/P1 基础能力：

- [ ] 所有任务有可机读的目标、范围、约束和验收标准。
- [ ] 关键业务不变量由独立验收测试覆盖，不只由 Coder 自己生成测试。
- [ ] 每个任务在隔离工作区执行；外部文本不能直接授权工具操作。
- [ ] PR 运行环境默认没有生产密钥和包发布权限。
- [ ] API/CLI 工具调用有 schema 校验、错误类型、受控重试和审计日志。
- [ ] CI、Review、Merge、Deploy 分别追踪，真实状态来自外部系统。
- [ ] 测试报告能定位到实际 `head_sha` 和环境摘要。
- [ ] 长任务有 Checkpoint、修复次数上限和中断恢复机制。
- [ ] 代码 Review 检查业务逻辑、重复度、异常处理和越界修改。
- [ ] 能量化每个“有效完成任务”的全部成本与人工参与时间。
- [ ] 有代表真实项目的滚动 Eval 集，并记录测试环境/验证器版本。
- [ ] 线上故障能自动回灌为新的回归测试或限制策略。

## 11. 研究结论与推荐投资顺序

1. **第一投入：验证器和需求契约**。它决定 Agent 的“成功”是否真实；修好这层，才能放心提高自主执行比例。
2. **第二投入：安全边界和工具网关**。Agent 越能执行现实世界动作，越需要独立、确定性的授权和运行时限制。
3. **第三投入：仓库上下文与环境可复现**。这是减少高频误改、虚构依赖和工具失败的直接抓手。
4. **第四投入：长任务状态机与证据链**。这是多小时、多 PR 和无人值守生产必需的控制面。
5. **第五投入：基于真实仓库的评测与成本模型**。它决定哪些任务可以自动合并，哪些必须由人介入，以及是否真正降低了总成本。

**最重要的原则**：不要把“模型能继续尝试”误认为“系统可持续可靠”。可靠性来自 **明确的工作契约 + 受控的工具能力 + 外部独立验证 + 可审计的交付事实**。

---

## 12. 参考文献与可核对来源

- **[R01]** Stack Overflow. *Developer Survey 2026 — Technology / AI mistake costs*, 2026. 调查原始数据；n=13,648（该题，多选）。https://survey.stackoverflow.co/2026/technology/data
- **[R02]** Zhang, R. et al. *Engineering Pitfalls in AI Coding Tools: An Empirical Study of Bugs in Claude Code, Codex, and Gemini CLI*, 2026，公开 PDF/预印本样式（含出版信息占位）。3,864 个已关闭核实 Bug，数据截至 2025-12-12。https://www.eecs.yorku.ca/~wangsong/papers/fse26-industry.pdf
- **[R03]** Columbia DAPLab. *9 Critical Failure Patterns of Coding Agents*, 2026-01-08。15+ 应用、5 种工具，质性失效分析。https://daplab.cs.columbia.edu/general/2026/01/08/9-critical-failure-patterns-of-coding-agents.html
- **[R04]** OpenAI. *Separating signal from noise in coding evaluations*, 2026-07-08。SWE-bench Pro 问题审计；不能把估计比例当所有基准的缺陷率。https://openai.com/index/separating-signal-from-noise-coding-evaluations/
- **[R05]** Scale AI. *SWE-Bench Pro V2*, 2026-09-22。任务清洗、干净环境复评、验证协议。https://labs.scale.com/leaderboard/swe_bench_pro_public_v2
- **[R06]** Jin, Q. et al. *ChainSWE: Benchmarking Coding Agents on Multi-Bug Software Maintenance*, 2026。304 Issue / 54 项目；任务链相关性能退化。https://arxiv.org/abs/2607.02606
- **[R07]** Cynthia, S. T. et al. *Beyond Bug Fixes: An Empirical Investigation of Post-Merge Code Quality Issues in Agent-Generated Pull Requests*, MSR 2026。1,210 个已合并 Agent Bug-fix PR。https://arxiv.org/abs/2601.20109
- **[R08]** DORA / Google. *Balancing AI tensions: Moving from AI adoption to effective SDLC use*, 2026-03-10；基于 DORA 2025 和工程师反馈。https://dora.dev/insights/balancing-ai-tensions/
- **[R09]** Microsoft Defender Security Research. *Securing CI/CD in an agentic world: Claude Code Github action case*, 2026-06-05。带有复现实证的 CI/CD 安全研究。https://www.microsoft.com/en-us/security/blog/2026/06/05/securing-ci-cd-in-agentic-world-claude-code-github-action-case/
- **[R10]** OWASP. *Agentic Skills Top 10*, 2026；公开审议中的风险分类与实践建议。https://owasp.github.io/www-project-agentic-skills-top-10/
- **[R11]** Veracode. *Fall 2026 GenAI Code Security Update*, 2026-10。样本限定于所测模型、四种语言和四类 CWE；平均安全通过率约 62%，**不可解释为生产代码 38% 一定有漏洞**。https://www.veracode.com/blog/fall-2026-genai-code-security
- **[R12]** GitClear. *The Maintainability Gap: 2026 AI Code Quality Research*, 2026。大规模代码变更趋势研究，观察性非因果。https://www.gitclear.com/the_ai_code_quality_maintainability_gap
- **[R13]** Columbia DAPLab. *Coding Agents Keep Shipping Silent Failures — Here Is How to Catch Them*, 2026-09-18。UI 与状态管理的静默故障案例。https://daplab.cs.columbia.edu/general/2026/09/18/flowcheck-catching-silent-failures.html
- **[R14]** Bai, W. et al. *When Passing Tests Hides Vulnerabilities: An Empirical Study of Silent Failures in Agentic Systems*, 2026。1,030 条执行轨迹中鉴定 170 个安全静默失败（研究样本与模型限制明显）。https://arxiv.org/abs/2609.10548
- **[R15]** Krentsel, A. et al. *Reality Is the Final Verifier: On Two Key Gaps in Agentic Software Engineering*, 2026。需求落差与环境模型落差框架。https://arxiv.org/abs/2609.12039
- **[R16]** METR. *We are Changing our Developer Productivity Experiment Design*, 2026-02-24。强调当前生产率估计偏差；切勿外推 2025 实验。https://metr.org/blog/2026-02-24-uplift-update/
- **[R17]** Albayaydh, W. et al. *Beyond the Leaderboard: A Synthesis of Tool-Use, Planning, and Reasoning Failures in Large Language Model Agents*, 2026。综述 27 篇相关研究、19 个基准。https://arxiv.org/abs/2607.05775
- **[R18]** Dai, W. et al. *A Large-Scale Empirical Study of Quality Assurance Practices and Gaps in AI Agents*, 2026。157 个开源 Agent 项目，测试保护不均匀。https://arxiv.org/abs/2609.17698

### 12.1 本次解决方案调研新增的官方技术参考（S01—S20）

下列优先选用项目或组织的第一方技术文档。记录的是**该方案存在、支持哪些机制及限制**，并不直接证明在任何仓库上会提升特定百分比的成功率。

- **[S01]** Scale AI, *SWE-Bench Pro V2*（2026-09-22）：https://labs.scale.com/leaderboard/swe_bench_pro_public_v2
- **[S02]** OWASP, *LLM Prompt Injection Prevention Cheat Sheet*：https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- **[S03]** OWASP, *MCP Security Cheat Sheet*：https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html
- **[S04]** Model Context Protocol, *One Year of MCP: November 2025 Spec Release*（授权扩展参考）：https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/
- **[S05]** OpenAI, *Agent approvals & security*：https://learn.chatgpt.com/docs/agent-approvals-security
- **[S06]** GitHub, *About protected branches / required checks*：https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- **[S07]** GitHub, *Securely using pull_request_target*：https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
- **[S08]** Anthropic, *Claude Code Settings files and precedence*：https://code.claude.com/docs/en/settings
- **[S09]** Playwright, *Assertions and auto-retrying*：https://playwright.dev/docs/test-assertions
- **[S10]** Hypothesis, *Quickstart and property-based tests*：https://hypothesis.readthedocs.io/en/latest/quickstart.html
- **[S11]** GitHub, *Artifact attestations*：https://docs.github.com/en/actions/concepts/security/artifact-attestations
- **[S12]** Aider, *Repository map*：https://aider.chat/docs/repomap.html
- **[S13]** Zoekt, *FAQ / indexing and code search*：https://github.com/sourcegraph/zoekt/blob/main/doc/faq.md
- **[S14]** Astral, *uv Locking and syncing*：https://docs.astral.sh/uv/concepts/projects/sync/
- **[S15]** LangGraph, *Checkpoint reference*：https://langchain-ai.github.io/langgraph/reference/checkpoints/
- **[S16]** Temporal, *Activity Definition / idempotency*：https://docs.temporal.io/activity-definition
- **[S17]** GitHub, *Code scanning with CodeQL*：https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning
- **[S18]** GitHub, *Managing a merge queue*：https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- **[S19]** LiteLLM, *Router, retries, fallbacks and cooldowns*：https://docs.litellm.ai/docs/router/learn/reliability
- **[S20]** OpenTelemetry, *GenAI semantic conventions*：https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/

**核验记录：** 本次新增参考均于 2026-11-17 检索第一方资料并核对关键机制；配置参数、服务套餐、文档路径可能发生变化，实际安装前应再次核对对应软件版本。部分原报告 [R] 来源为研究论文/预印本，保持原有证据等级与限制，不把框架可行性推断成已证实的改善率。

---

## 13. 限制与待验证问题

- 本研究是公开证据综合，不是对某一组织私有 CI、Issue 与 Agent Trace 的现场审计；**不能据此声称任何特定仓库发生了相同故障**。
- 问卷、Issue、benchmark、威胁研究和代码提交挖掘有不同样本/分母/选择偏差；不可把数字相加或直接用于生成“行业统一失败率”。
- 部分 2026 研究仍为预印本或观察性研究；涉及第三方安全检测的报告具有厂商选样和方法偏差。
- 实际“最大瓶颈”的优先级须结合项目类型、风险、编程语言、仓库规模和当前 CI 覆盖，经 30 天真实任务评测确认。

**版本：v2.0｜最后核验：2026-11-17**

**更新记录：** v2.0 保留原 2026 年实证研究和 16 项故障分类，新增 §4A 共 16 项逐项解决方案、§4A.17 选型矩阵、§6A 工程实施配方与故障注入矩阵、20 项官方技术参考；全部示意代码均标明生产适配边界。