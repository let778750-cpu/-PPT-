---
name: experiment-diagram-maker
description: 为深度学习实验报告和 PPT 制作可追踪的流程图、模型结构图、数据流图、结果图和表格图。适用于报告或 PPT 需要 draw.io 流程图、算法结构图、训练曲线、混淆矩阵、指标对比图等可视化资产，并需要把图源文件、导出图和证据映射登记到 `_workflow` 的场景。
---

# 实验图表制作者

## 概述

在报告写作前或 PPT 生成前使用这个 skill。
它负责把验证过的实验事实转成可复用图表资产，并登记到 `_workflow`，供 `experiment-report-writer` 和 `experiment-ppt-writer` 引用。

## 输入

- `workflow_state.yaml`
- `artifacts_manifest.yaml`
- `execution_log.md`
- 实际源码、指标文件、训练历史、评估输出
- 可选：draw.io MCP 工具、Python 绘图库、LaTeX TikZ

## 输出

返回结构化结果：

```yaml
diagram_result:
  status:
  created_assets:
    - path:
      kind:
      supports: []
  missing_assets: []
  notes:
```

允许的 `status` 值：

- `completed`
- `partial`
- `blocked`

## 推荐资产

至少优先准备以下资产：

- 算法流程图：训练/评估/推理流程。
- 模型结构图：网络层次、张量形状、关键模块。
- 实验结果图：训练 loss/accuracy 曲线。
- 指标对比表：目标指标 vs 实际指标。
- 可选：混淆矩阵、样例预测图、消融对比图。

建议先在代码工作区保存可复现源产物，再按报告需要复制到报告包：

```text
code/workN code/figures/
  algorithm_flow.drawio
  algorithm_flow.pdf
  model_structure.drawio
  model_structure.pdf
  training_curve.pdf
  training_curve.svg
  metrics_table.pdf

实验报告/实验N/figures/
  algorithm_flow.pdf
  algorithm_flow.svg
  model_structure.pdf
  model_structure.svg
  training_curve.pdf
  training_curve.svg
```

报告需要引用时，复制或导出到 `实验报告/实验N/figures/`，不得写入 `实验报告模板_latex/figures/`。manifest 中必须保留源产物路径和报告引用路径的对应关系。

## 工具选择

按优先级选择：

1. draw.io MCP：适合算法流程图、模型结构图、数据流图。保留 `.drawio` 源文件并优先导出 PDF 矢量图，同时可保留 SVG。
2. Python 绘图库：适合训练曲线、混淆矩阵、指标条形图。数据必须来自已登记的 metrics 或 history 文件，优先导出 PDF 矢量图并保留 SVG 副本。
3. LaTeX TikZ：适合简单流程图或无外部工具时的 fallback。

不要用无法复现的数据手动画图。

## 图表规范

- 每个图表必须有明确标题和用途。
- 中文图中文字保持简洁，字号适合报告和 PPT 双重使用。
- 结果图必须标注数据来源。
- 指标图必须展示目标值和实际值。
- 图表不能包含未验证指标。
- 图源文件和导出文件都应登记到 manifest。
- 正式报告优先使用矢量图。只有截图、样例预测图等天然位图内容才使用 PNG，且应保证清晰度不低于 300 DPI。

## 执行流程

1. 读取 verifier 输出，确认可视化数据来源。
2. 确定报告/PPT 缺少的关键图表。
3. 为每个图表建立 `supports` 列表，关联 requirement、metric、command 或 artifact。
4. 生成图源文件和导出图。
5. 检查图文件是否实际存在、可读、路径为相对路径。
6. 更新 `_workflow/artifacts_manifest.yaml` 和 `workflow_state.yaml`。

## 状态追踪交接

manifest 中的图表条目建议使用：

```yaml
- id: artifact-fig-001
  path: figures/training_curve.png
  kind: figure
  produced_by_phase: phase4_verification
  produced_by_command: cmd-train-mnist
  supports:
    - metric-001
  exists: true
  sha256:
  verified_at:
  notes:
```

## 失败处理

- 指标文件不存在：返回 `blocked`，要求回到 verifier 补齐。
- 图表只完成部分：返回 `partial`，列出缺失图表。
- draw.io 不可用：使用 Python 或 TikZ fallback，但仍需登记源和导出文件。

## 边界

这个 skill 不得：

- 虚构训练曲线、混淆矩阵或指标对比。
- 改写 verifier 指标。
- 为了美观删除失败结果或限制说明。
- 代替 report writer 或 ppt writer 撰写正文。
