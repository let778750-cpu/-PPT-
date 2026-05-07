---
name: experiment-code-baseline
description: 在代码实现开始前检查实验代码工作区的现状。适用于已经确定 `code_dir` 后，需要识别现有代码结构、入口脚本、测试覆盖、已有产物、关键缺口和实施起点，并输出代码基线摘要与初步实现计划的场景。
---

# 实验代码基线检查器

## 概述

在实验实现开始之前使用这个 skill。
它只负责理解目标代码工作区的当前状态，识别已有基线、缺口与实现起点，并输出结构化结论，供后续实现阶段使用。

如果 `code_dir` 还是空工作区，这不是错误；此时应明确识别“当前无实现基线”。
不要用这个 skill 去真正修改代码、运行正式训练、做指标验收，或撰写报告。

## 输入

- `code_dir`
- `code_dir_state`
- 可选的 `requirement_summary`

## 输出

返回两个结构化结果：

```yaml
baseline_summary:
  workspace_state:
  entry_points: []
  package_layout: []
  structure_compliance:
    status:
    missing: []
    risks: []
  tests_present:
  test_files: []
  outputs_present:
  output_files: []
  data_present:
  data_files: []
  observed_but_unverified_artifacts: []
  known_gaps: []
  risks: []

implementation_plan:
  starting_mode:
  target_layout:
    package_dir:
    entry_scripts: []
    output_dirs: []
  priority_tasks: []
  files_to_create: []
  files_to_modify: []
  notes:
```

允许的 `workspace_state` 值：

- `empty`
- `partial`
- `usable`
- `unclear`

允许的 `starting_mode` 值：

- `from_scratch`
- `extend_existing`
- `repair_existing`
- `clarify_first`

## 检查流程

1. 确认 `code_dir` 是否存在，以及当前是否已有文件结构。
2. 检查是否存在 README、训练脚本、评估脚本、环境检查脚本、依赖文件、测试目录、数据目录和输出目录。
3. 识别主要入口脚本和核心包结构。
4. 检查是否已经存在测试文件、历史模型产物或运行结果。
5. 对照标准实验代码布局，判断当前工作区是结构化、平铺、部分结构化还是混乱。
6. 结合 `requirement_summary`，判断当前代码与实验要求之间的主要缺口。
7. 输出代码基线摘要和初步实现计划。

## 检查建议

- 先看目录结构，再看入口脚本，再看测试与输出。
- 优先识别：
  - `README.md`
  - `train_*.py`
  - `evaluate_*.py`
  - `check_environment.py`
  - `requirements.txt`
  - `tests/`
  - `data/`
  - `outputs/`
- 如果存在模块化包目录，如 `mnist_cnn/`，记录其核心模块角色。
- 标准布局应接近 `code/work1 code/`：根目录保留 `README.md`、`requirements.txt`、`check_environment.py`、`train_<task>.py`、`evaluate_<task>.py`，核心逻辑放入一个实验专属 snake_case 包目录，测试放 `tests/`，训练产物放 `outputs/`，图表放 `figures/`，状态放 `_workflow/`。
- 如果核心逻辑主要平铺为根目录级 `model.py`、`data.py`、`train.py`、`evaluate.py`，应在 `structure_compliance.risks` 中标记 `flat_layout`，并在 `implementation_plan` 中建议迁移到包目录。
- 如果已有产物存在，不默认它们可信；登记为 `observed_but_unverified_artifacts`，后续必须由 verifier 重新验证。
- 如果已有 `data/` 目录或数据文件存在，不默认它们来源正确；登记为 `data_present` 和 `data_files`，后续必须由数据就绪检查确认。
- 如果工作区为空，应明确给出 `starting_mode: from_scratch`。

## 字段规则

- `baseline_summary.workspace_state`：当前工作区整体状态
- `baseline_summary.entry_points`：可见的主要脚本入口
- `baseline_summary.package_layout`：核心包和模块结构
- `baseline_summary.structure_compliance.status`：`compliant`、`partial`、`flat_layout`、`missing` 或 `unclear`
- `baseline_summary.structure_compliance.missing`：相对标准布局缺失的目录或文件类别
- `baseline_summary.structure_compliance.risks`：结构偏离带来的维护、测试或报告资产风险
- `baseline_summary.tests_present`：`true` 或 `false`
- `baseline_summary.test_files`：已有测试文件列表
- `baseline_summary.outputs_present`：`true` 或 `false`
- `baseline_summary.output_files`：已有输出文件或模型产物
- `baseline_summary.data_present`：`true` 或 `false`
- `baseline_summary.data_files`：已有数据目录、压缩包或数据摘要文件
- `baseline_summary.known_gaps`：和实验要求相比已知缺失项
- `baseline_summary.risks`：潜在风险、可疑点、需要后续验证的地方
- `implementation_plan.starting_mode`：从零开始、在现有基础上扩展、修复现有实现，或先澄清
- `implementation_plan.target_layout`：后续实现阶段应落成的包名、入口脚本和输出目录
- `implementation_plan.priority_tasks`：后续实现阶段最优先要做的事
- `implementation_plan.files_to_create`：建议新建的文件
- `implementation_plan.files_to_modify`：建议重点修改的文件

## 输出规则

- 结果必须紧凑、结构化、面向后续实现阶段。
- 只描述当前事实和初步计划，不做具体代码设计。
- 如果存在已有实现，不得自动认定“已经可用”。
- 如果工作区为空或接近空，应明确说明，而不是写成模糊描述。
- 入口脚本、测试文件、已有产物和 README 等关键文件应交给 `experiment-state-tracker` 登记到产物清单。

## 状态追踪交接

基线检查完成后，使用 `skills/experiment-state-tracker/SKILL.md` 更新：

- `_workflow/workflow_state.yaml` 中的 `baseline_summary` 和 `implementation_plan`
- `_workflow/artifacts_manifest.yaml` 中的入口脚本、测试文件、README、依赖文件和已有产物
- `_workflow/workflow_state.yaml` 中与当前实验要求相关的缺口和风险

已有输出文件只能登记为“存在”，不得登记为“已验证”，除非后续 verifier 重新验证。

## 失败处理

- 如果 `code_dir` 路径异常或无法访问，使用 `workspace_state: unclear`。
- 如果现有结构与实验需求之间缺口很大，可用 `starting_mode: from_scratch` 或 `repair_existing`。
- 如果缺少关键信息导致无法判断下一步，使用 `starting_mode: clarify_first`。

## 边界

这个 skill 不得：

- 修改任何代码文件
- 运行正式训练、评估或指标验收
- 决定最终模型细节
- 代替环境核验
- 生成实验报告或 PPT
