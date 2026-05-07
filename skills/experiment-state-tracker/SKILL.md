---
name: experiment-state-tracker
description: 维护深度学习实验的跨阶段状态、证据链、产物清单和执行日志。适用于每个实验阶段开始或结束时，需要创建或更新 `code/workN code/_workflow/workflow_state.yaml`、`artifacts_manifest.yaml`、`execution_log.md`，以及在报告、PPT 和最终交付前核验结果是否有真实命令、指标和文件支撑的场景。
---

# 实验状态追踪器

## 概述

在每个实验阶段开始和结束时使用这个 skill。
它负责把路由结果、PDF 要求、环境事实、代码基线、实现变更、测试训练评估结果、报告产物串成可追踪证据链。

这个 skill 不替代任何业务阶段；它只维护状态文件、产物清单和执行日志，保证后续报告不能引用没有证据支撑的结果。

## 状态文件位置

每个实验的状态文件必须保存在该实验专属代码工作区中：

```text
code/workN code/_workflow/
  workflow_state.yaml
  artifacts_manifest.yaml
  execution_log.md
```

初始化时可复制本 skill 的模板：

```text
skills/experiment-state-tracker/assets/workflow_state.template.yaml
skills/experiment-state-tracker/assets/artifacts_manifest.template.yaml
skills/experiment-state-tracker/assets/execution_log.template.md
```

规则：

- `N` 必须等于真实实验编号。
- 如果 `code/workN code/` 不存在，在实验路由已唯一匹配后创建它，再创建 `_workflow/`。
- 不要把多个实验的状态写入同一个 `_workflow/`。
- 不要把状态文件放在项目根目录或其他实验目录。

## 文件职责

`workflow_state.yaml` 保存当前实验的最新结构化状态。
它回答：当前做到哪一阶段、PDF 提出了什么要求、哪些要求已实现或验证、哪些问题仍阻塞。

`artifacts_manifest.yaml` 保存所有关键产物的索引。
它回答：哪些文件支撑了代码、测试、训练、评估、报告中的事实，它们由哪个阶段或命令产生。

`execution_log.md` 保存按时间顺序排列的执行记录。
它回答：运行过什么命令、在哪个目录运行、目的是什么、结果如何、产生了哪些证据文件。

## 初始化流程

1. 在路由阶段得到 `experiment_id`、`experiment_name`、`pdf_path`、`code_dir` 后，创建或更新 `_workflow/`。
2. 若状态文件不存在，创建最小骨架。
3. 若状态文件已存在，先读取并保留历史事实，只追加或更新当前阶段相关字段。
4. 如果状态文件与当前路由结果冲突，停止并报告冲突，不要静默覆盖。

最小 `workflow_state.yaml`：

```yaml
schema_version: 1
experiment:
  experiment_id:
  experiment_name:
  pdf_path:
  code_dir:
  code_dir_state:
  requirement_dir:
  companion_files: []
  status: initialized
phase_status:
  phase1_router:
    status:
    updated_at:
    outputs: {}
requirements:
  items: []
provided_assets: []
dataset_requirements:
  name:
  source_type:
  required_files: []
  local_assets: []
  external_source_needed:
  notes: []
data_readiness:
  status:
  source_type:
  source_paths: []
  data_dir:
  checked_by_command:
  summary:
runtime_profile: {}
baseline_summary: {}
implementation: {}
verification:
  status:
  overall_passed:
  metrics: []
  command_ids: []
  report_assets: []
diagrams:
  assets: []
report:
  claims: []
  review: {}
ppt:
  brief_path:
  slides: []
  outputs: []
open_issues: []
```

最小 `artifacts_manifest.yaml`：

```yaml
schema_version: 1
artifacts: []
```

最小 `execution_log.md`：

```markdown
# Execution Log

Experiment:
```

## Requirement 证据规范

从 PDF 提取出的每条关键要求都应有稳定 ID，并尽量记录来源。

```yaml
- id: req-001
  type: required_task
  text:
  source:
    file:
    page:
    section:
    quote:
  status: pending
  supports: []
```

规则：

- `type` 使用 `objective`、`required_task`、`hard_constraint`、`target_metric`、`deliverable`、`theory_scope`。
- `quote` 只放短摘或转述，避免大段复制 PDF。
- 如果无法确定页码，写 `page: unknown`，并在 `open_issues` 记录原因。
- 硬性指标必须单独建成 `target_metric` 项，不要只写在摘要段落里。

## 命令日志规范

每次运行会影响判断的命令，都要写入 `execution_log.md`。

记录模板：

```markdown
## cmd-YYYYMMDD-HHMMSS-name

- Phase:
- CWD:
- Command:
- Purpose:
- Status: success | failed | partial | skipped
- Exit code:
- Started:
- Finished:
- Key output:
- Artifacts:
- Notes:
```

规则：

- 环境检查、测试、训练、评估、LaTeX 编译必须记录。
- 不要记录无关的探索命令，除非它影响阶段结论。
- `Command` 应保留可复现命令，包括解释器、参数和工作目录。
- 长输出只摘关键行；完整日志如有价值，应保存为文件并登记到 manifest。

## 产物清单规范

关键文件必须登记到 `artifacts_manifest.yaml`。

```yaml
- id: artifact-001
  path:
  kind:
  produced_by_phase:
  produced_by_command:
  supports:
    - req-001
  exists:
  sha256:
  verified_at:
  notes:
```

`kind` 建议值：

- `source_code`
- `test_file`
- `environment_log`
- `training_log`
- `evaluation_log`
- `checkpoint`
- `metrics_json`
- `run_summary`
- `dataset_archive`
- `dataset_raw`
- `dataset_processed`
- `dataset_source_record`
- `data_preparation_log`
- `figure`
- `vector_figure`
- `diagram_source`
- `diagram_export`
- `vector_diagram`
- `report_tex`
- `report_pdf`
- `ppt_brief`
- `ppt`

规则：

- 对报告将引用的指标文件、日志、模型权重、图表、报告 PDF 必须登记。
- `sha256` 在文件稳定且计算成本合理时填写；大模型文件可留空并说明。
- `supports` 指向 requirement ID、metric ID 或 claim ID。
- 文件不存在时不得登记为已验证产物，应写 `exists: false` 并记录问题。

## 阶段更新规则

Phase 1 路由完成后：

- 写入 `experiment`。
- 写入 `requirement_dir`、`pdf_path` 和 `companion_files`。
- 写入 `phase_status.phase1_router`。
- 如果路由不唯一，不创建实验状态，只在对话中报告歧义。

Phase 2 PDF 解析完成后：

- 写入 `requirements.items`。
- 写入 `provided_assets` 和 `dataset_requirements`，包括本地伴随数据资产、标准数据集或外部开源数据需求。
- 为硬性约束、指标和提交物建立稳定 ID。
- 将无法定位来源或表述不清的问题写入 `open_issues`。

Phase 3 环境和基线完成后：

- 写入 `runtime_profile` 和 `baseline_summary`。
- 将检查命令写入 `execution_log.md`。
- 将环境日志、README、测试文件、历史结果等关键文件登记到 manifest。

Phase 5 实现完成后：

- 写入 `implementation` 和 `phase_status.phase5_implementation`。
- 将新增或修改的源码、测试、README、依赖文件登记到 manifest。
- 将数据准备/检查脚本、数据来源记录和本地伴随数据资产登记到 manifest。
- 将实现阶段 sanity command 写入 `execution_log.md`。
- 将仍未覆盖的 requirement 写入 `open_issues` 或 `implementation.requirement_coverage.pending`。

Phase 6 验证与图表资产完成后：

- 先写入 `data_readiness`，记录数据来源、数据目录、检查命令和摘要。
- 写入修改摘要、测试结果、训练结果、评估指标。
- 每个指标必须指向产生它的命令和支撑文件。
- 未通过的测试或未达标指标必须写入 `open_issues`。
- 写入 `verification.status` 和 `verification.overall_passed`。
- 将 `metrics_json`、`run_summary`、训练曲线、模型结构图、流程图等报告/PPT 资产登记到 manifest。
- 图源文件使用 `diagram_source`，导出图使用 `diagram_export` 或 `figure`。

Phase 7 报告生成前：

- 检查报告将声明的每个关键结论是否能追溯到 `requirements.items`、`execution_log.md` 和 manifest。
- 没有证据的结论不得写入报告。
- 报告 `.tex` 和 `.pdf` 写入 manifest。
- 报告复核结果写入 `report.review`。
- 报告复核通过只表示 Phase 7 完成；不得把实验任务标为最终交付，必须继续进入 Phase 8。

Phase 8 PPT 生成前：

- Phase 8 是完整实验任务的必做最后阶段，不以用户是否额外要求 PPT 为条件。
- 只允许引用已经进入报告或 verification 的事实。
- `ppt_brief.md` 必须登记为 `ppt_brief`。
- 每页 slide 的结论应写入 `ppt.slides`，并关联 requirement、metric、command 或 artifact。
- PPT 文件写入 manifest。

## 报告前核验

进入报告阶段前，必须能回答：

- PDF 哪一页或哪个章节提出了该要求？
- 哪个代码文件实现了该要求？
- 哪条命令验证了该要求？
- 指标值来自哪个日志或结果文件？
- 报告中的结论由哪些 artifact 支撑？

如果任何关键结论回答不了，返回前一阶段补证据；不要用推测补齐。

## PPT 前核验

进入 PPT 阶段前，必须能回答：

- 报告是否已经生成并复核通过？
- PPT 每一页的核心结论来自哪个 requirement、metric、command 或 artifact？
- 图表是否已经登记到 manifest 且文件存在？
- `ppt_brief.md` 是否列出页面结构、证据映射和禁用内容？

如果任何 slide 的核心结论无法追踪，先补 `ppt_brief.md` 或回到报告/验证阶段补证据。

## 最终交付核验

任务结束前，使用状态文件做一次轻量交付核验：

- 代码工作区必须是当前实验唯一对应的 `code/workN code/`。
- 测试、训练、评估命令必须记录在 `execution_log.md`。
- 数据来源、数据准备/检查命令和数据目录摘要必须记录在 `data_readiness` 与 manifest；正式训练不得是第一次触发数据下载。
- 硬性指标必须来自已登记日志或指标文件。
- 报告 `.tex`、`.pdf`、编译日志、图表和证据副本必须登记到 manifest。
- 报告产物应位于 `实验报告/实验N/`；模板目录不得承载具体实验报告正文。
- `ppt_brief.md`、PPTX 和关键页面产物必须登记到 manifest；PPT 缺失时不得声明完整交付。
- 若仍有残留问题，必须写入 `open_issues`，最终回复不得把它们描述成已解决。

项目根目录可使用 `tools/workflow_consistency_check.py` 做机器检查：

```bash
python tools/workflow_consistency_check.py .
```

该检查应覆盖 `_workflow` 三件套、manifest 中声明存在的文件、报告/PPT 路径、`running` 残留状态和 completed 阶段的关键产物。发现 error 时必须先修复，再交付。

## 边界

这个 skill 不得：

- 虚构运行结果、指标或文件
- 代替 PDF 解析、代码实现、测试训练评估或报告写作
- 把失败结果改写成成功状态
- 删除历史执行日志
- 静默覆盖与当前实验不一致的状态文件
