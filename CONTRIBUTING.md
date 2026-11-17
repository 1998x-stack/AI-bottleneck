# Contributing / 研究贡献指南

欢迎提交：新领域研究、现有 Issue 的证据补充、方案成熟度修正、实际复现实验或 UI 改进。

### 研究准则
- **可核验**：数据有统计口径、来源、发布日期；论文和厂商宣发分开标注。
- **可证伪**：每个解决方案写明适用边界、失败案例和验收指标。
- **可扩展**：行业独立 ID；Issue ID 在所属领域稳定，不跨领域共用本地含义。
- **不编造**：没有系统实测数据就标注为估算、访谈或研究判断。

### PR 交付要求
- 报告原文与 catalog 一致
- 新增来源有稳定 ID 和 HTTPS 链接
- `node scripts/validate.mjs` 通过
- `python scripts/build_site.py` 通过
- Web UI 的搜索、筛选、报告阅读与移动端没有退化

参考 [数据合约](docs/data-contract.md) 与 [UI 设计](docs/ui-design.md)。
