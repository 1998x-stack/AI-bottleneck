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


## v2 实施说明：跨领域与文档衍生物

- `catalog/index.json` 的 `domains` 列表只存已发布领域，`planned` 列表不可计入统计。
- Issue ID 只需领域内唯一；全局标识使用 `domainId/issueId`，例如 `ai-coding/CA-01`。
- `sourceIds` 始终指向本领域的 `catalog/sources/<domain>.json`；同一 `S01` 在两个领域不表示同一来源。
- `reports[].path` 指向 Git 内真实 Markdown 源文档；站点构建衍生 `downloads/<report.id>.docx` 和 `.pdf`，站点不依赖外部 PDF URL。
- `publications/<domainId>/` 可以镜像生成的 Word/PDF 文件用于 Git 历史留存；这些是衍生物，Markdown + Catalog 仍是唯一可编辑源。
- 扩展字段使用可选策略，不能在不升级 `schemaVersion` 的情况下破坏 v1 必填字段。
- 所有来源需有类型与 URL；公开调查百分比与工程风险优先级禁止直接进行算术比较。
