---
name: experiment-verifier
description: 对已实现的实验代码执行正式测试、训练、评估，验证指标是否达标。适用于 `experiment-code-implementer` 完成代码实现并交接后，需要在 `code/workN code/` 中运行单元测试、训练脚本、评估脚本，将真实指标与 PDF 要求对比，并将验证结果写入 `_workflow` 状态文件的场景。
---

# 实验验证器

## 概述

在 Phase 6 的验证部分使用这个 skill。
它负责接收 `experiment-code-implementer` 的交接结果，执行正式的单元测试、训练、评估命令，收集真实指标，与 PDF 要求中的硬性指标对比，并将验证结论写入 `_workflow` 状态文件。

这个 skill 不修改源代码。如果验证过程中发现代码错误，应将问题记录到 `open_issues` 并建议返回 implementer 修复。

## 前置条件

进入验证前，必须确认：

- `code/workN code/_workflow/workflow_state.yaml` 存在且 `phase5_implementation.status` 不是 `blocked`
- 实现器已提供 `verifier_handoff`，包含 `recommended_commands`、`expected_metrics` 和 `risks`
- 训练和评估所需的入口脚本实际存在
- 环境已通过 `check_environment.py` 验证
- 代码目录采用标准实验代码布局：根目录有 README、requirements、环境检查、训练入口、评估入口；核心逻辑位于实验专属包目录；测试、输出、图表和 `_workflow` 目录分离

如果前置条件未满足，返回 `blocked` 并说明缺失项。

## 输入

- `code_dir`
- `requirement_summary`
- `target_metrics`
- `verifier_handoff`（来自 implementer）
- `code/workN code/_workflow/workflow_state.yaml`
- `code/workN code/_workflow/artifacts_manifest.yaml`
- `code/workN code/_workflow/execution_log.md`

## 输出

返回结构化验证结果：

```yaml
verification_result:
  status:
  data_readiness:
    status:
    source_type:
    data_dir:
    command:
    summary:
  test_result:
    passed: true | false
    total:
    failed:
    command:
  train_result:
    completed: true | false
    command:
    epochs:
    best_metric: {}
    output_files: []
  evaluation_result:
    completed: true | false
    command:
    metrics: {}
  report_assets:
    metrics_json:
    run_summary:
    figures: []
  metrics_summary:
    - id:
      name:
      value:
      target:
      met: true | false
  overall_passed: true | false
  failed_items: []
  recommendation:
  notes:
```

允许的 `status` 值：

- `passed` — 所有硬性指标达标
- `partial` — 部分指标达标，部分未达标
- `failed` — 关键指标未达标
- `blocked` — 无法执行验证（环境错误、脚本缺失等）
- `needs_fix` — 发现代码错误，需返回 implementer

## 验证流程

1. 读取 `_workflow/workflow_state.yaml`，确认实验编号和当前状态。
2. 读取 `verifier_handoff.recommended_commands`，规划执行顺序。
3. 读取 `verifier_handoff.expected_metrics`，明确验证标准和阈值。
4. 按以下顺序执行验证步骤：

### 步骤 0：结构合规检查

- 检查 `README.md`、`requirements.txt`、`check_environment.py`、训练入口、评估入口、`tests/`、`outputs/` 或其约定等是否存在。
- 检查是否至少存在一个实验专属 snake_case 包目录，且包内包含模型、数据、训练/评估工具等核心模块。
- 如果核心逻辑主要平铺在根目录级 `model.py`、`data.py`、`train.py`、`evaluate.py`，且没有包目录，状态设为 `needs_fix`，建议返回 implementer 整理为标准布局。
- 如果只缺少可由验证过程生成的 `outputs/`、`outputs/logs/` 或 `figures/`，可以创建或登记，但必须记录到执行日志。
- 结构检查通过后，才能进入环境复检和长时间训练。

### 步骤 1：环境复检

- 运行 `check_environment.py` 或等价命令，确认 GPU、CUDA、依赖库可用。
- 如果环境不可用，状态设为 `blocked`，停止验证。

### 步骤 2：数据就绪检查

- 读取 Phase 2 的 `dataset_requirements` 和 Phase 5 的 `data_preparation`。
- 如果存在本地伴随数据资产，确认 prepare/check 命令使用该资产，而不是绕过本地文件另行下载。
- 运行 `verifier_handoff.recommended_commands` 中的数据准备或数据检查命令。
- 确认真实训练/评估数据目录存在，关键文件、样本数、类别/字段摘要可被检查命令输出或写入日志。
- 如果数据缺失、来源不明、下载失败或只准备了 synthetic/mock 数据，状态设为 `blocked` 或 `needs_fix`，不得进入正式训练。
- 数据准备命令可以下载或解压；正式训练和评估命令不得隐式下载数据。

### 步骤 3：单元测试

- 运行 `verifier_handoff.recommended_commands` 中的测试命令。
- 记录通过/失败数量。
- 如果测试全部失败或关键测试失败，状态设为 `needs_fix`，建议返回 implementer。
- 如果少量非关键测试失败，记录到 `failed_items` 但继续验证。

### 步骤 4：训练

- 运行 `verifier_handoff.recommended_commands` 中的训练命令。
- 监控训练过程，确认：
  - 训练正常完成所有 epoch
  - loss 持续下降（允许个别 epoch 波动）
  - 输出文件（checkpoint、history）实际产生
- 如果训练中途崩溃，记录错误信息，状态设为 `needs_fix`。
- 如果训练完成但输出文件缺失，记录问题，状态设为 `partial`。

### 步骤 5：评估

- 运行 `verifier_handoff.recommended_commands` 中的评估命令（如有）。
- 从评估输出或 `history.json` 等指标文件中提取最终指标。
- 将提取的指标与 `target_metrics` 逐一对比。

### 步骤 6：指标判定

- 对每个 `target_metric`，判断 `actual_value` 是否满足 `target` 条件。
- 全部达标：`overall_passed: true`。
- 部分未达标：`overall_passed: false`，在 `failed_items` 中列出未达标项。
- 关键硬性指标未达标不得标为 passed。

### 步骤 7：报告/PPT 资产整理

- 将最终指标写入 `outputs/metrics.json` 或等价文件；如果脚本已产出类似文件，复用并登记。
- 将关键命令、环境、超参数、最佳指标和产物路径整理为 `outputs/run_summary.md` 或等价文件。
- 如果训练历史存在，生成或登记训练曲线；如果分类任务有混淆矩阵或样例预测图，也应登记。
- 资产不足时不要虚构，写入 `report_assets` 的缺失项和 `open_issues`。

### 步骤 8：状态更新

- 将验证结果写入 `_workflow/workflow_state.yaml` 的 `verification` 部分。
- 将训练产物和指标文件登记到 `_workflow/artifacts_manifest.yaml`。
- 将所有执行的命令写入 `_workflow/execution_log.md`。
- 将未达标指标或发现问题写入 `open_issues`。

## 执行规范

- 所有命令必须在 `code_dir`（即 `code/workN code/`）下执行。
- 命令必须保留完整可复现形式，包括解释器路径和所有参数。
- 正式训练前必须完成结构合规检查；结构不合规时不要用长时间训练掩盖目录和职责混乱。
- 正式训练前必须完成数据就绪检查；不要让训练脚本第一次加载数据时才开始下载或解压。
- 正式训练和评估推荐命令必须使用 `--no-download` 或等价离线选项；如脚本不支持，应记录为 `needs_fix`。
- 训练命令前必须确认 GPU 可用（除非实验明确使用 CPU）。
- 训练产出应写入 `outputs/` 或实验约定目录。
- 长时间训练命令应设置合理超时，超时后记录为 `blocked` 并说明原因。
- 不要为了通过验证而修改源代码、超参数或指标阈值。

## 指标提取规则

- 指标必须从实际命令输出或产出文件中提取，不得凭记忆或推测填写。
- 如果指标文件格式与预期不符，记录实际情况并尝试解析。
- 如果某个指标无法提取，在 `failed_items` 中说明原因，不要填入虚假值。
- 训练曲线（loss、accuracy 等）应保留完整的逐 epoch 记录。
- 报告和 PPT 使用的指标必须优先引用已登记的 metrics 文件，而不是只引用对话中的摘要。

## 重试策略

如果验证失败但原因可能是环境或随机因素：

- 允许最多重试一次训练命令（不同随机种子）。
- 重试必须记录到 `execution_log.md`，标注为重试。
- 重试结果无论好坏都必须如实记录。
- 不要无限重试直到指标达标。

如果重试后仍未达标：

- 如实记录连续失败结果。
- 将问题写入 `open_issues`。
- 建议返回 implementer 检查模型结构或超参数。

## 状态追踪交接

验证完成后，使用 `skills/experiment-state-tracker/SKILL.md` 更新：

- `_workflow/workflow_state.yaml` 中的 `verification`（metrics、command_ids）
- `_workflow/workflow_state.yaml` 中的 `data_readiness`
- `_workflow/workflow_state.yaml` 中的 `phase_status.phase6_verification`
- `_workflow/artifacts_manifest.yaml` 中训练和评估产出的文件（checkpoint、metrics JSON 等）
- `_workflow/artifacts_manifest.yaml` 中数据来源记录、数据准备日志和数据目录摘要
- `_workflow/artifacts_manifest.yaml` 中报告/PPT 资产（run summary、figures、diagram exports）
- `_workflow/execution_log.md` 中所有验证阶段执行的命令
- `_workflow/workflow_state.yaml` 中的 `open_issues`（如有）

验证结果将作为 Phase 7 报告生成的直接依据。报告只能引用 verifier 已确认的指标和产物。

## 失败处理

- 环境不可用：`status: blocked`，建议检查环境配置。
- 数据未就绪或来源不明：`status: blocked`，先完成数据准备或返回 implementer 增加数据准备入口。
- 单元测试全部失败：`status: needs_fix`，建议返回 implementer 检查代码。
- 训练崩溃：`status: needs_fix`，附上错误信息。
- 训练完成但指标未达标：`status: partial` 或 `failed`，如实记录实际指标与差距。
- 评估脚本运行错误：`status: needs_fix`，附上错误信息。
- 产出文件缺失：记录缺失项，状态设为 `partial`。

## 边界

这个 skill 不得：

- 修改源代码、模型结构、超参数或训练配置
- 虚构或篡改训练指标
- 降低指标阈值以使验证通过
- 跳过失败的测试或训练步骤
- 删除之前的训练日志或 checkpoint 以掩盖失败
- 生成最终实验报告或 PPT
- 修改其他实验工作区的文件
