---
name: experiment-report-reviewer
description: 在 Phase 7 结束前复核实验报告真实性、证据链、结构完整性、图表质量和 LaTeX 编译结果。适用于 `experiment-report-writer` 已生成 `.tex` 和 `.pdf` 后，需要检查报告是否覆盖 PDF 要求、是否引用真实验证结果、是否存在未追踪结论、图表/公式/代码是否合规，并给出报告是否可进入 Phase 8 PPT 阶段的场景。
---

# 实验报告复核器

## 概述

在报告生成后、进入 Phase 8 PPT 前使用这个 skill。
它以审稿方式检查报告是否真实、完整、可编译、可追溯，不负责重写整篇报告。
报告复核通过不等于完整实验交付；通过后必须继续生成和复核 PPT。

## 前置条件

- `phase7_report.status == completed` 或报告文件已生成但需要复核。
- 报告 `.tex`、`.pdf` 文件实际存在。
- `_workflow` 三件套存在。
- 报告中的主要图表、指标和代码引用已登记到 manifest。

## 输入

- 报告 `.tex`
- 报告 `.pdf`
- `workflow_state.yaml`
- `artifacts_manifest.yaml`
- `execution_log.md`
- 实验要求 PDF
- 实际源码和指标文件

## 输出

返回结构化复核结果：

```yaml
report_review:
  status:
  blocking_issues: []
  warnings: []
  coverage:
    requirements_checked:
    claims_traced:
    figures_checked:
  compilation:
    pdf_exists: true | false
    latex_log_checked: true | false
  recommendation:
  notes:
```

允许的 `status` 值：

- `approved`
- `needs_revision`
- `blocked`

## 复核清单

优先检查以下项目：

- PDF 要求是否全部覆盖。
- 硬性指标是否来自 verifier 真实输出。
- 数据集来源、样本规模、文件路径和预处理描述是否来自 `dataset_requirements`、`data_readiness` 或已登记数据准备日志。
- 报告中的每个关键结论是否登记在 `report.claims`。
- 每个 claim 是否能追溯到 requirement、command、metric 或 artifact。
- 图表文件是否存在、可读、标题和正文引用一致。
- 图表 caption 是否使用 `图 X. ...`、`表 X. ...` 句点分隔；不得出现冒号分隔。
- 报告正文是否优先引用 PDF/SVG 矢量图；若引用 PNG，需确认其属于必要位图且清晰度足够。
- "一、实验内容"是否只描述实验任务和要求，不包含公式环境、形式化定义或损失函数推导。
- 训练曲线、混淆矩阵、指标表是否来自真实文件。
- 报告是否把外部开源数据集写清楚来源和许可/使用说明；不得把训练时隐式下载的数据写成已预先准备。
- 算法描述是否与实际源码一致。
- 公式符号是否前后一致。
- 代码片段是否来自真实实现，且不是整文件堆砌。
- LaTeX 是否使用 XeLaTeX 成功编译，PDF 是否最新。
- 总结是否如实说明失败尝试、限制或未达标项。
- 参考文献部分是否另起一页（检查 `.tex` 中是否使用了 `\experimentsectionpage{参考文献}` 或等价的 `\clearpage` 命令）。
- "参考文献"标题是否左对齐、黑体小三（与其他一级标题格式一致，而非 `thebibliography` 默认的居中标题）。
- 参考文献标题与首条文献之间的间距是否与前四个章节标题与正文的间距一致（检查是否通过 `\renewenvironment{thebibliography}` 移除了内置 `\section*`，而非仅用 `\renewcommand{\refname}{}`）。
- 参考文献引用格式是否严格遵循项目根目录 `references.bib` 模板中定义的标准格式：全名作者（≤ 3 人全部列出最后一位前用 `and`，> 3 人列出前 3 位后接 `et al.`）、sentence case 标题、期刊/会议名用 `\emph{}`、条目末尾英文句点。
- 每条参考文献的类型（期刊/会议/书籍/学位论文/技术报告/预印本/在线资源/软件/数据集/标准）是否与 `references.bib` 中对应类型的格式模板一致，不得混用不同类型的字段。
- 参考文献是否均为真实权威的学术文献（可在 Google Scholar 检索）或官方技术文档，不存在虚构或低质量引用。
- "四、实验总结"末尾是否有覆盖整个实验全貌的总结性收尾段（需包含实验目标回顾、核心方法回顾、关键结果回顾和整体收获，而非仅停留在结果分析层面）。

## 阻塞问题

出现以下情况必须返回 `blocked`：

- 报告引用了不存在或未登记的指标。
- 报告引用了不存在、来源不明或未完成训练前检查的数据集。
- 报告宣称达标，但 verifier 未达标或没有验证记录。
- 报告 PDF 不存在或无法打开。
- 关键实验要求完全未覆盖。
- 发现明显虚构的命令、结果或图表。

## 一般警告

以下情况返回 `needs_revision`：

- 页码来源不完整但不影响核心结论。
- 图表质量不足或缺少流程图。
- 图表仍使用可替代的低清晰度位图。
- 图表编号分隔符不是句点。
- 第一部分出现应放入实验原理的公式推导。
- 代码片段过长或说明不足。
- 结论表述太口语化、缺少定量分析。
- 参考文献未另起一页，或"参考文献"标题未左对齐，或标题与文献条目间距与前四章节不一致。
- 参考文献引用格式与项目根目录 `references.bib` 模板不一致（非全名作者、作者数量未按 ≤3 全列 / >3 截断为前 3 位 + et al. 的规则处理、非 sentence case 标题、期刊/会议名未用 `\emph{}`、条目末尾缺少英文句点等）。
- 参考文献条目类型与 `references.bib` 中对应类型格式模板不匹配（如会议论文缺少 `booktitle`、期刊论文缺少 `volume`/`pages` 等）。
- 参考文献中存在非权威或疑似虚构的引用。
- "四、实验总结"缺少全实验总结性收尾段（仅有结果分析而缺少对整个实验全流程的概括回顾）。
- `report.claims` 不够细，但核心指标仍可追踪。

## 状态追踪交接

复核完成后，使用 `experiment-state-tracker` 更新：

- `workflow_state.yaml` 中的 `report_review`。
- `execution_log.md` 中的报告复核记录。
- 如有修订后的报告文件，更新 manifest 的 sha256 和 `verified_at`。
- 将下一步明确标记为 Phase 8 PPT 生成，不要把报告复核通过写成最终交付完成。

## 边界

这个 skill 不得：

- 把未通过的报告标记为可进入 Phase 8。
- 把报告复核通过标记为完整实验任务已交付。
- 虚构缺失证据。
- 删除失败结果来让报告看起来更好。
- 代替 verifier 重新判定指标。
