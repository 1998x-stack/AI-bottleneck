# AI Bottleneck Observatory · Web UI / UX Design System v2

> 2026-11-17 · 面向持续接入 AI 小说、短剧、Coding Agent、知识库、音乐等研究领域。此文区分 **已实施** 与 **未来计划**；不是产品效果声明。

## 1. 产品定位

AI Bottleneck Observatory 是持续生长的**跨领域产业问题、证据与解决方案研究库**，不是某份 PDF 的静态展示。目标用户包括研究员、架构师、独立开发者、技术产品经理及内容产业从业者。

核心 Jobs-to-be-done：
- 对一个行业：在 60 秒内判断其主要生产瓶颈、P0 风险和已有研究解决路径；
- 对一个问题：查看其症状、根因、既有研究、限制、可衡量的验收指标；
- 对一种技术：跨领域查询适用场景，避免将论文原型误写成商业成熟方案；
- 对一份报告：在线阅读、章节导航、引用追溯、下载 MD/DOCX/PDF；
- 对贡献者：按统一契约加入全新行业，不修改前端核心代码。

**原则：** 研究证据优先，视觉层次明确，导航快速，版本可追踪，默认公开可访问，不引入账号与在线业务数据库。

## 2. 信息架构 IA

```text
Research Observatory
├── Overview（主页）
│   ├── Cross-domain KPIs（领域/Issues/报告/来源数）
│   ├── Domain Discovery（领域卡片：短剧、小说、未来 ...）
│   ├── Featured Domain（当前选择领域的摘要）
│   └── Research Coverage Matrix（各领域收录量，不代表真实发生率）
├── Issues Atlas（按当前领域）
│   ├── 关键词全文筛选（题目/根因/已有方案/工具）
│   ├── Priority / Category / Maturity / Sort
│   └── Detail Drawer
│       ├── 症状 → 根因 → 方案 → 局限 → 验收
│       ├── 证据跳转
│       └── 跳转完整版研究报告
├── Reports（按当前领域）
│   ├── 版本档案（v1 → v2；不可覆写历史结论）
│   ├── 在线 Markdown Reader + 文章目录
│   └── Download: Markdown / Word / PDF
├── Evidence（按当前领域）
│   └── 按来源类型和关键词检索，HTTPS 一键打开
└── Methodology（跨领域共同规则）
    └── 证据分层、优先级、成熟度、测量与扩展合约
```

当前跨域编码为 `?domain=ai-fiction&view=issues&issue=NV-01`。不使用 hash 作为唯一导航状态，以便链接可复制、浏览器后退恢复。全球搜索结果点击时同步切换其所属领域。过往单领域 URL 未带 domain 时默认选第一个领域，保持向后兼容。

## 3. 视觉语言

- 视觉意象：Research OS / Field Notes / Observatory；使用实验室笔记、精细网格、数据标签与专业档案的语汇。
- 中性色为背景；强调色使用现有青绿色 `--accent`，P0 使用暖色，亮/暗主题均满足辨识。
- 字体：中文优先 Noto Sans SC 的网络字体回退到系统字体；数值编号使用 IBM Plex Mono；字号建立 11/13/15/18/24/32 档。
- 空间：8/12/16/24/32 的间距节奏。卡片圆角与轻阴影，不依赖大面积饱和色框承载总结。
- 布局：上方固定品牌与主导航，首屏是有可读价值主张的 Hero，随后进入“侧边目录 + 内容区”工作台。
- 当前专题高亮：左侧领域按钮以及首页领域卡片均有一致的选中态，避免“看着是短剧、读的却是小说”的错配。
- 信息密度：关键数量以数字标签显示，文本遵循标题 → 核心症状 → 根因 → 方案 → 证据 → 验收顺序，不把长篇资料平铺成巨大卡片墙。

## 4. 核心页面与交互规格

### 4.1 Overview / 领域入口
**已实施：** 可选择已发布领域、跨领域 KPIs、专题摘要、P0 列表、报告档案、研究数量对照矩阵。矩阵说明其数字是**本项目已收录量**，不以其判断行业真实频率。

**未来：** 支持按技术栈/产线阶段的跨行业对比；需要先定义通用分类本体，避免不同领域直接比严重度。

### 4.2 Issue Atlas / 问题图谱
**已实施：** 关键词、P0/P1/P2、研究类别、M0–M3 成熟度、排序；结构化 Issue 卡片点击打开详情抽屉。深链接 `issue=<id>` 可直达问题。

**交互细节：** 输入筛选即时生效；结果区显示命中数与总数；零结果给出恢复指引；抽屉提供关闭按钮、Esc 与背景点击关闭；复制问题 URL 后可在同一领域重新打开。问题内容包含 2–3 条可操作路线，不只列产品名。

### 4.3 Research Reports / 版本档案
**已实施：** MD、DOCX、PDF 下载入口；站内 Markdown 阅读器、H1/H2 导航；PDF/Word 在构建时由 Markdown 源文件生成。小说保留 v1 瓶颈报告与 v2 完整解决方案手册。

**质量要求：** 每个下载 URL 都经 CI 检查文件存在且非空；报告的 `date` 与 `version` 是研究版本，不会因为前端迭代被隐式修改。

### 4.4 Evidence Register / 证据登记
**已实施：** 独立来源表（URL、标题、类型、使用场景），支持搜索和 research/policy/report/tool 四类筛选，所有外链用 `noopener noreferrer`。

**研究规范：** 证据等级不能仅凭来源类型判断；论文实验、官方规则、工具官网、行业观察应做显式区分。

### 4.5 Global Search / 全域搜索
**已实施：** 搜索全部已发布专题中的问题、根因、技术方案和工具；支持斜杠 `/` 与 Ctrl/⌘+K；点击结果会切换到所属领域。全局 Issue key 是 `domainId/issueId`，不同领域内短编号不得在路由处理时互相覆盖。

**未来：** 领域数量超过几十个、目录数据超过浏览器允许的快速初始加载体积时，改用静态预生成倒排索引与惰性加载；不默认接入需支付费用的搜索 SaaS。

## 5. 无障碍 / Responsive / Performance

- 桌面端优先双列卡片，窄屏时单列；侧边导航与按钮必须可键盘操作。
- 保留 `skip-link`、label/aria 描述、焦点可见样式与站内状态 `aria-live`。
- 减少动效偏好时禁止卡片位移动效；亮暗主题保留对比度。
- 抽屉作为 dialog，进一步上线前应加入完整的 focus trap 与焦点还原（**目前未声称已完整实现**）。
- 站点使用静态 HTML/CSS/JS，不把用户阅读数据发送外部跟踪服务；外部字体可按需迁移到本地资源以满足完全离线的隐私要求。
- 各站点资源基于 `import.meta.url` 相对定位，确保 GitHub Pages 的 `/AI-bottleneck/` 子路径不会导致 404。

## 6. 内容模型与可扩展性

```text
catalog/index.json
catalog/domains/<domain-id>.json
catalog/sources/<domain-id>.json
reports/<domain-id>/<slug>.md
reports/<domain-id>/<slug>.docx [generated]
reports/<domain-id>/<slug>.pdf  [generated]
```

禁止在 app.js 中写死领域名称或某一报告的 ID。领域接入只修改 index、domain、sources、reports；前端自动生成导航、筛选器、下载链接和来源列表。

管理性字段：`schemaVersion`、`status`、`updatedAt`、`issueCount`、`sourceIds`；研究论断必须在 Markdown 中有可核验的依据。双主键 `domainId/issueId` 避免跨领域 ID 碰撞。

## 7. 文档构建和发布路径

1. PR 中提交 Markdown 和 Catalog，运行 Node schema 验证、JS 语法检查和 Python 构建。
2. 构建时用 python-docx 将 Markdown 渲染为 DOCX，再用 LibreOffice 转为 PDF；同时检查四个下载文件：两个小说报告 × 两种二进制格式。
3. Pages workflow 部署 `dist/`，报告下载文件位于 `dist/downloads/<id>.docx|pdf`。
4. `pages.yml` 在主分支构建并将 DOCX/PDF 保存至 `reports/<domain>/exports/`、生成 SHA256 manifest 后提交回主分支，满足长期 Git 存档（需要 Actions contents:write）。
5. 最终验收不能只看 commit，必须检查 PR CI、主分支 deploy job、GitHub Pages URL、线上下载 URL、PDF 实际页数与中文版式。

**注意：** 自动生成 Word 与上一轮会话的手工排版版式不保证逐字逐页相同；Markdown 内容是统一来源。

## 8. 上线验收矩阵

| 场景 | 操作 | 应有结果 |
|---|---|---|
| 初次访问 | 打开根目录 | 展示多领域概况，没有编造的“已发布”领域 |
| 切换领域 | 从短剧点“AI 小说” | URL 带 `domain=ai-fiction`，卡片、Issue、来源、报告全部切换 |
| 直接问题链接 | 打开 `...view=issues&issue=NV-01` | 打开小说对应问题抽屉 |
| 全局搜索 | 搜索“故事记忆” | 小说问题命中，点击后切换领域 |
| 证据链接 | 打开任一来源 | HTTPS 新窗口，带安全 rel |
| 文件下载 | 点击 MD/DOCX/PDF | 下载文件非空，PDF 可打开并正常显示中文 |
| 浏览器历史 | 返回 / 前进 | 选中领域与视图恢复 |
| 移动端 | 390px 宽 | 卡片单列，无横向溢出；表格可横向滚动 |
| 无障碍 | Tab/Shift-Tab/Esc | 所有关键交互可达、焦点可见、抽屉可关闭 |
| 内容扩展 | 添加新 domain JSON | 无需修改核心 app.js 即可出现在站点 |

## 9. 近期工程问题（后续迭代）

P0：保证 Pages 和二进制报告同步真正成功；为数据/文档生成加校验与日志。
P1：完善 Markdown 阅读器对表格与代码的排版，增加正文页内检索、主题对照、来源证据等级筛选。
P1：用 Playwright 在 CI 运行桌面/移动/Esc/浏览器历史/下载链接 E2E。
P2：数据域增加 evidence quality、更新历史、owner、reviewed_at、benchmark fixture 等字段；迁移至 v2 Schema 时提供兼容层。
P2：100+ 领域后使用分块索引、预编译站点搜索与静态页面预渲染，而不是一次 `Promise.all` 请求所有档案。
