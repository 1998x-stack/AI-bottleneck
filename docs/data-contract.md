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
    "date": "2026-11-17",
    "artifacts": {
      "docx": "reports/ai-short-drama/exports/unique-report-id.docx",
      "pdf": "reports/ai-short-drama/exports/unique-report-id.pdf"
    }
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

## 版本化 Word / PDF 归档规范

每份已发布报告必须声明 `reports/<domainId>/exports/<reportId>.docx` 与 `.pdf`；这些是**正式的 Git 仓库文件**，不是 Pages 暂存产物。自动构建为每个领域生成同目录的 `manifest.json`，记录 Markdown 来源及 DOCX/PDF SHA-256。CI 中 `scripts/verify_exports.py` 检查源文档变更、文档完整性、PDF 页数及 Pages 下载副本的字节级一致性。报告更新后重新生成的文件由 Actions 自动提交到主分支。


## Cross-domain UI and traceable routing (2026-11-17)

- Across-domain issue identity: `<domainId>/<issueId>`, not an issue ID by itself.
- `?domain=ai-coding&view=issues&issue=CA-01` links preserve domain context.
- Only `domains` contribute to published statistics; `planned` is excluded.
- External evidence is a cited research reference, not necessarily validation of a tool's real-world effectiveness.
- Report Word/PDF artifacts are committed to `reports/<domainId>/exports/`, with SHA256 manifest checks and byte-for-byte matching Pages downloads.
