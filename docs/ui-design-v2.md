# AI Bottleneck Observatory · Web UI v2 与可扩展发布架构
## 产品目标
把「跨行业长篇研究」转为可索引、可追证、可比较、可下载的研究操作台。所有行业遵循相同的视觉语言，保留行业独立上下文。
## 信息架构
1. **总览**：领域范围、Issue 数、报告数、引用源数量；精选 P0。
2. **多领域导航**：左侧领域列表具有活动态；?domain=<slug> 可直链与历史前进/后退。
3. **问题图谱**：P0/P1/P2、分类、成熟度、排序和关键词过滤。Issue 详情显示症状→根因→方案→局限→验收→引用。
4. **研究报告**：版本、日期、Markdown 原文、Word、按需 PDF 下载；完整阅读器附目录导航。
5. **证据库**：每领域独立来源登记；从 Issue 反向链接到官方规范或研究。
6. **全站搜索**：任意领域问题可检索；跳转时必须先切换领域再打开 Issue，避免跨领域同 ID 冲突。
## 交互与视觉
- 色彩：深海蓝/薄荷绿的研究仪表盘，少量暖橙标记风险；亮色/暗色双主题。
- 桌面：顶部全局导航、左侧研究领域、主栏卡片与阅读器、右侧不强制开栏，阅读页保留目录。
- 移动端：顶栏简化、侧栏顺序进入内容区、卡片单列、抽屉全屏易关闭；键盘 / 与 Ctrl/Cmd+K 搜索。
- 可访问性：可见焦点、Esc 关闭、可读色彩对比、语义按钮及 aria 标签。
## 数据/部署边界
- **静态前端**：HTML/CSS/ES Modules；无数据库、无账号，GitHub Pages 子路径使用相对资源路径。
- **内容源**：reports/<domain>/*.md，catalog/domains 与 catalog/sources；规范通过 scripts/validate.mjs 检查。
- **发布物**：dist/downloads/*.docx + 所有报告均生成 PDF；企业知识库版本同步保存于 releases/enterprise-knowledge/。
- **权限**：GitHub Pages 是公开资料浏览，不应导入未脱敏企业资料或内部文档；站点不是企业知识系统本身。
- **验证**：Node 静态校验、Python 构建、LibreOffice PDF 导出、PDF 文件头检查、GitHub Actions Pages 发布状态检查。
## 继续扩展的路径
未来每个领域都只需加入 Markdown 报告、source registry、domain JSON、index registry 条目；所有领域报告都生成 Word/PDF，分别归档到 reports/<domain>/exports 并记录 SHA256。
## 后续 UI 里程碑
- P1：跨领域对照视图，比较同类根因、解决方式与证据强度；不把类别不同的指标作未经解释的直接比较。
- P1：静态全文索引与拼音别名；大型目录用分片搜索数据防止首屏加载全部报告。
- P2：引用位置与 DOI 校验、站内 SVG 知识流程图、数据导出 CSV、国际化。
- P2：版本变化可视化、审稿状态和自动引用链接健康检测。
