# AI Bottleneck Observatory / AI 产业瓶颈研究图谱

> Research is a process, not a PDF. 让复杂的产业问题变成可检索、可追溯、可对比、可验证的工程路线。

[GitHub Pages](https://1998x-stack.github.io/AI-bottleneck/) · [问题图谱](https://1998x-stack.github.io/AI-bottleneck/?view=issues) · [研究报告](https://1998x-stack.github.io/AI-bottleneck/?view=reports) · [证据库](https://1998x-stack.github.io/AI-bottleneck/?view=evidence)

**状态：** 当前已导入 **AI 短剧** 专题（12 个 DR issues、33 条来源、2 份完整 Markdown 研究报告）。其他领域显示为**规划中**，不冒充已完成研究。

## 产品定位

这不是单次生成报告的展示页，而是可增长的**跨行业 AI 生产瓶颈知识库**：

- 从「现象与严重度」进入「技术根因」，逐项对应「已有工具/方法」、「适用边界」、「验收指标」和「证据来源」。
- 单一领域报告与结构化问题索引同时存在；研究更新可追溯，不以模型宣传值代替实测指标。
- 全站搜索、问题筛选、详情抽屉、文档阅读、来源登记、明暗主题、响应式布局。
- 使用 GitHub Pages 发布，**前端无框架依赖、无数据库、无账号系统**；每加入一个行业不需要重写前端。
- GitHub Actions 校验 JSON schema 合约、引用、报告文件，构建 Word 下载版本并部署 Pages。

## 目录

```text
├── index.html               # 网页壳与 SEO
├── styles.css               # 响应式视觉设计
├── app.js                   # 页面、路由、筛选和交互
├── markdown.js              # 安全转义的离线 Markdown 阅读器
├── assets/
│   └── favicon.svg
├── catalog/
│   ├── index.json           # 所有已发布/规划领域入口
│   ├── domains/
│   │   └── ai-short-drama.json # Issues、解决方案、指标及报告清单
│   └── sources/
│       └── ai-short-drama.json # 编号证据来源
├── reports/
│   └── ai-short-drama/
│       ├── bottlenecks-2026-11-17.md
│       └── solutions-2026-11-17.md
├── scripts/
│   ├── validate.mjs        # 跨领域合约和引用校验
│   └── build_site.py       # 静态打包与生成 Word
├── docs/
│   ├── architecture.md
│   ├── data-contract.md
│   ├── ui-design.md
│   └── roadmap.md
├── .github/workflows/pages.yml
├── CONTRIBUTING.md
└── AGENTS.md
```

## 本地运行

需要 Node.js 22+、Python 3.10+；浏览器通过 HTTP 访问（不能直接双击 index.html）。

```bash
git clone https://github.com/1998x-stack/AI-bottleneck.git
cd AI-bottleneck
node scripts/validate.mjs
python3 -m http.server 8000
# 访问 http://localhost:8000/
```

生成与 GitHub Pages 一致的静态站点（包含 Word 下载）：

```bash
python3 -m pip install python-docx==1.2.0
python3 scripts/build_site.py
cd dist && python3 -m http.server 8000
```

## 新增领域（例如 AI Coding Agent）

1. 将完整 Markdown 报告放在 `reports/ai-coding/`；引用采用稳定 ID，例如 `[S01]`。
2. 基于 `docs/data-contract.md` 创建 `catalog/domains/ai-coding.json` 和 `catalog/sources/ai-coding.json`。
3. 将 `{"id":"ai-coding","path":"catalog/domains/ai-coding.json"}` 添加到 `catalog/index.json` 的 `domains` 数组，删除其 `planned` 条目。
4. 运行 `node scripts/validate.mjs` 和 `python scripts/build_site.py`。
5. 提交 PR；合并后 Actions 更新 Pages，无需修改 `app.js` 或 `styles.css`。

## GitHub Pages 首次启用

该仓库使用 GitHub Actions 自定义部署。若首次运行 deploy 作业失败，仓库维护者需到 **Settings → Pages → Build and deployment → Source → GitHub Actions** 选择发布源，然后在 **Actions** 中重跑 `Validate and deploy Research Pages`。仓库有 Workflow 并**不保证** Pages 已经启用；必须以部署成功和实际网址可访问为准。

推荐站点 URL：`https://1998x-stack.github.io/AI-bottleneck/`

## 方法与边界

研究材料发布日期和适用范围以原报告为准；P0/P1/P2 是工程优先级判断，M0/M1/M2/M3 是建议性的方案成熟度描述，**不是某个权威机构的统一等级**。任何工具能力、价格与政策信息在采购、商业发布和法律决策前均需重新核验。

见 [数据合约](docs/data-contract.md)、[Web UI 设计](docs/ui-design.md) 与 [研发路线](docs/roadmap.md)。

## 许可

研究文档引用的第三方资料受其各自权利声明约束；引用与链接并不代表获得第三方素材的再发行许可。站点代码可以进一步采用明确的开源 LICENSE 后对外授权；在仓库指定许可证前，不应默认允许无限制复制和商业再使用。
