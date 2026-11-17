# Roadmap / 可扩展研究库演进

## Milestone 0 — Foundation
- [x] 空仓库初始化与研究框架
- [x] AI 短剧 v1 + v2 完整 Markdown
- [x] 12 Issue + 33 Source 结构化目录
- [x] 可检索 Web UI 与报告阅读器
- [x] CI 验证与 GitHub Pages 发布工作流
- [ ] GitHub Pages 首次启用及线上成功部署确认（由部署结果决定）

## Milestone 1 — Multi-domain (next)
- [ ] 新增 AI Coding Agent 领域报告、Issue 映射、证据索引
- [ ] 新增企业知识库领域
- [ ] 新增 AI 小说 / 新闻视频领域
- [ ] 领域选择器与跨领域差异矩阵
- [ ] 全站搜索的分组结果和来源去重

## Milestone 2 — Evidence Quality
- [ ] 证据等级、来源类型、审查状态和核验日期
- [ ] 结论-来源-实验的关系图
- [ ] 过期来源自动核验提醒（应单独授权，不依赖 Pages）
- [ ] JSON Schema 正式文件及数据迁移流程

## Milestone 3 — Research Operating System
- [ ] Issue 与 GitHub 项目/PR 的状态联动
- [ ] 解决方案案例与失败实验库
- [ ] 跨行业公共瓶颈分类（长上下文、资源治理、质量门禁等）
- [ ] 同领域不同时间版本的变化追踪
- [ ] 数据导出（CSV / JSON）与定期公开快照

**原则：** 不为规模化提前引入数据库。先验证跨领域 JSON 模型能够满足前 3–5 个行业，再决定是否需要 API 和 CMS。
