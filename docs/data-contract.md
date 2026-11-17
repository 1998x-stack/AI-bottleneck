# Domain Data Contract / v1

所有 JSON 文件均为 UTF-8，直接通过 HTTPS/静态 Pages 分发。

## catalog/index.json
```json
{
  "schemaVersion": 1,
  "site": {"title":"AI Bottleneck Observatory","updatedAt":"2026-11-17"},
  "domains": [{"id":"ai-short-drama","path":"catalog/domains/ai-short-drama.json"}],
  "planned": [{"id":"ai-coding","title":"AI Coding Agent","description":"规划中"}]
}
```

## catalog/domains/<id>.json
```json
{
  "schemaVersion": 1,
  "id": "ai-short-drama",
  "title": "AI 短剧",
  "titleEn": "AI Short Drama",
  "description": "领域说明",
  "updatedAt": "2026-11-17",
  "status": "published",
  "categories": ["视觉一致性", "生产工程"],
  "issueCount": 1,
  "reports": [{
    "id": "unique-report-id",
    "version": "v1.0",
    "label": "研究标题",
    "description": "本版覆盖范围",
    "path": "reports/ai-short-drama/file.md",
    "date": "2026-11-17"
  }],
  "issues": [{
    "id": "DR-01",
    "title": "问题标题",
    "category": "视觉一致性",
    "priority": "P0",
    "maturity": "M2",
    "summary": "外部症状或业务损失",
    "rootCause": "本质原因",
    "symptoms": ["异常1"],
    "solutions": [{"name":"方法","approach":"实施方案","limitations":"局限","tools":["VACE"]}],
    "metrics": ["验收指标1"],
    "sourceIds": ["S01"]
  }]
}
```

## catalog/sources/<id>.json
```json
{"schemaVersion":1,"domainId":"ai-short-drama","sources":[
 {"id":"S01","title":"论文或报告","note":"适用信息和限制","url":"https://example.org","type":"research"}
]}
```

`type` 可取 `research`、`policy`、`report`、`tool`。等级 `priority` ∈ P0/P1/P2，`maturity` ∈ M0/M1/M2/M3。编号在领域内唯一；不同领域可以重用 DR-01 等短编号，前端与跨域分析时以 `<domainId>/<issueId>` 为全局键。

### 强制校验
`node scripts/validate.mjs` 负责检查 ID 唯一性、引用存在、来源 HTTPS、报告路径与实际文件存在、类别和枚举合法性。更严格的 schema 和跨域统计在后续迭代引入。

## 扩展说明（v1 兼容）

- `index.domains` 可注册任意数量的领域；前端使用 `?domain=<slug>` 保留选中领域。
- 所有 `reports[]` 都生成 Word/PDF，版本化文件和 SHA256 清单在 `reports/<domain>/exports/`，部署工作流需要 LibreOffice 和中文字体。
- 完整 Markdown 与 `catalog/domains/<slug>.json` 是分离的：前者用于完整阅读和下载，后者用于筛选、Issue 抽屉和跨领域搜索。
- 研究中标注的 M2/M3 为现有方案可集成性评估，不代表问题已在任何具体企业消除。
- 新领域的 Issue ID 在领域内唯一，跨领域引用使用 `<domain>/<issue>`。

## 领域可选扩展字段：AI Music (向后兼容)

音乐 Issue 保留 `originalId`（MUS-001…MUS-020），站内短 ID 为 MU-01…MU-20，允许 GitHub Issue 与研究源稿双向映射。

- `issues[].sop`: 可执行步骤数组；仅当存在时在详情抽屉显示。
- `issues[].verification` / `evidenceLevel` / `residualRisk`: 研究证据与验收辅助说明，不代表实测故障发生率。
- `reports[].artifacts.docx` 和 `reports[].artifacts.pdf`: 合约要求其值为 `reports/<domain>/exports/<reportId>.<ext>`，CI 校验。
- 每个领域由独立的 `catalog/domains/<domain>.json` 和 `catalog/sources/<domain>.json` 维护，旧领域无需升级字段；不做跨行业优先级“统计排行榜”的误导性推断。
