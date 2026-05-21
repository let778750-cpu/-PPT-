---
name: experiment-code-implementer
description: 按国科大深度学习实验要求实现或修正代码。适用于已经完成实验路由、PDF 要求解析、环境核验和代码基线检查后，需要在 `code/workN code/` 中创建或修改模型、数据处理、训练脚本、评估脚本、测试和 README，并把实现结果交给 verifier 正式测试训练评估的场景。
---

# 实验代码实现器

## 概述

在 Phase 5 的实现部分使用这个 skill。
它负责把 `requirement_summary`、`runtime_profile`、`baseline_summary` 和 `implementation_plan` 落成可运行代码，并准备后续验证所需的测试、训练和评估入口。

这个 skill 可以创建和修改代码文件，但不能替代 verifier 宣称测试通过、训练完成、指标达标，也不能撰写最终实验报告。

## 输入

- `code_dir`
- `requirement_summary`
- `target_metrics`
- `deliverables`
- `runtime_profile`
- `baseline_summary`
- `implementation_plan`
- `code/workN code/_workflow/workflow_state.yaml`
- `code/workN code/_workflow/artifacts_manifest.yaml`
- `code/workN code/_workflow/execution_log.md`

## 输出

返回结构化实现结果：

```yaml
implementation_result:
  status:
  mode:
  changed_files: []
  created_files: []
  requirement_coverage:
    covered: []
    partial: []
    pending: []
  entry_points:
    environment_check:
    tests:
    train:
    evaluate:
  prepared_artifacts:
    output_dirs: []
    expected_files: []
    expected_report_assets: []
  data_preparation:
    source_type:
    source_paths: []
    prepare_command:
    check_command:
    train_requires_no_download: true | false
  code_layout:
    package_dir:
    entry_scripts: []
    test_dir:
    output_dirs: []
  sanity_commands: []
  verifier_handoff:
    recommended_commands: []
    expected_metrics: []
    risks: []
  notes:
```

允许的 `status` 值：

- `ready_for_verification`
- `partial`
- `blocked`
- `needs_clarification`

允许的 `mode` 值：

- `from_scratch`
- `extend_existing`
- `repair_existing`

## 实现流程

1. 读取 `_workflow/workflow_state.yaml`，确认 `code_dir`、实验编号、PDF 和当前任务一致。
2. 读取 `requirement_summary`、`target_metrics`、`deliverables` 和 `implementation_plan`。
3. 明确本阶段写入范围，只在该实验的 `code/workN code/` 内创建或修改文件。
4. 如果 `code_dir` 不存在且路由已唯一匹配，可以创建该目录；不得创建其他实验目录。
5. 检查现有文件，理解已有入口脚本、包结构、测试和 README，避免覆盖用户已有工作。
6. 将关键要求转成实现清单，并尽量关联 `_workflow` 中的 requirement ID。
7. 按实现清单补全或修正：
   - 数据加载和预处理
   - 数据准备或数据检查入口
   - 模型结构
   - 训练循环
   - 评估逻辑
   - 保存和加载模型产物
   - 指标 JSON、运行摘要、训练曲线等报告/PPT 资产接口
   - 配置、随机种子和命令行参数
   - 测试或 smoke test
   - README 中的可复现运行命令
8. 检查代码目录是否符合“标准实验代码布局”；不符合时先整理结构，再交给 verifier。
9. 运行轻量 sanity check 时，只用于确认代码可进入 verifier；正式测试、训练、评估和达标判断留给 verifier。
10. 更新 `_workflow` 状态、产物清单和执行日志。

## 实现原则

- 严格依据 PDF 要求和已提取的结构化要求实现，不为了“更高级”而偏离实验目标。
- 优先沿用现有代码风格、目录结构、命令入口和依赖管理方式。
- 从零实现或重建混乱实现时，必须采用类似 `code/work1 code/` 的结构化布局：根目录只保留少量入口脚本和项目说明，核心逻辑放入一个实验专属包目录，测试、输出、图表和 workflow 状态分别独立存放。
- 对 PDF 示例代码保持审慎：可以参考，但必须修正明显错误和不完整之处。
- 对深度学习实验，优先使用 PyTorch、torchvision、numpy 等既有库完成标准数据集、模型、训练和评估流程。
- 代码应能在 Windows 路径和带空格的目录中运行。
- 不要硬编码本机绝对路径；数据目录、输出目录、batch size、epoch、学习率等应通过合理默认值或 CLI 参数控制。
- 设置随机种子，并在可能时启用可复现选项。
- 训练输出、评估结果和 checkpoint 应写入该实验工作区内的 `outputs/` 或任务约定目录。
- 验证阶段要能稳定生成 `outputs/metrics.json` 或等价指标文件，以及必要时的 `outputs/run_summary.md`。
- 如果实验会产生曲线、混淆矩阵或样例预测图，应预留 `figures/` 或等价输出目录。
- 如果网络下载数据不是必需，应提供 `--no-download` 或等价选项。
- 正式训练命令不得隐式触发数据下载；下载、解压、复制、转换或校验必须通过独立数据准备/检查命令完成，并写入 `verifier_handoff.recommended_commands` 的训练命令之前。
- 在 Windows 上使用 DataLoader 多进程时要谨慎，默认可优先使用 `num_workers=0`。

## 数据来源与准备规则

数据准备遵循以下优先级：

1. **本地伴随数据资产优先**：如果 `实验要求（来自国科大在线）/实验N要求/` 中存在 `.zip`、`.npz`、`.csv`、`.txt`、`.json`、`.tar` 等数据文件，必须优先使用这些文件；不得绕过本地资产直接从网络下载同类数据。
2. **PDF 指定的标准数据集次之**：如果 PDF 指定 MNIST、CIFAR10 等标准公共数据集且本地无数据资产，可使用 torchvision 或官方工具准备数据，但准备动作必须独立于正式训练。
3. **外部开源数据最后**：如果 PDF 未给数据文件且也不是标准库数据集，必须先查找并确认官方、课程、论文或权威开源数据源，记录 URL、许可/使用说明和下载时间；不要使用来历不明的网盘、镜像或博客附件。

实现要求：

- 如果图像描述实验明确要求 MSCOCO，应优先使用官方 MSCOCO captions / instances 标注和官方图像 URL。完整数据过大时，可以构建官方采样子集，但必须固定随机种子、记录 train/val/test 图像数和 caption 数、保证验证集与测试集图像互斥，并在 README、报告和 `_workflow` 中如实说明。
- 从零实现时优先提供 `prepare_data_<task>.py` 或 `check_data_<task>.py`。至少要有一个命令能在正式训练前确认数据目录、样本数、类别/字段和关键文件存在。
- 本地伴随数据应复制或解压到 `code/workN code/data/` 下的清晰目录，如 `data/raw/`、`data/processed/`；原始文件路径和 sha256 应登记到 manifest。
- 训练脚本和评估脚本必须支持离线运行参数，例如 `--no-download` 或等价开关。
- `verifier_handoff.recommended_commands` 必须按顺序列出：环境检查、数据准备/数据检查、单元测试、正式训练、正式评估。
- 正式训练和评估推荐命令应使用 `--no-download` 或等价离线参数；只有数据准备命令可以联网下载，并且必须单独记录。
- synthetic/mock 数据只允许用于 sanity check，不得用于最终指标、报告或 PPT。

## 标准实验代码布局

后续所有实验代码应默认按下列模式组织，实验一的 `work1 code` 是参考实现：

```text
code/workN code/
  README.md
  requirements.txt
  check_environment.py
  train_<task>.py
  evaluate_<task>.py
  <task_package>/
    __init__.py
    data.py
    model.py
    engine.py
    utils.py
  tests/
    test_<task>.py
  outputs/
    logs/
  figures/
  _workflow/
    workflow_state.yaml
    artifacts_manifest.yaml
    execution_log.md
```

布局规则：

- `<task_package>` 必须是一个清晰的 snake_case 包名，例如 `mnist_cnn`、`vit_cifar10`、`poetry_transformer`；不要把核心实现长期平铺在工作区根目录。
- 根目录脚本只承担 CLI、配置解析和调用包内函数；模型、数据集、训练循环、评估指标、工具函数应在包目录中模块化实现。
- `tests/` 必须直接测试包内模块，而不是只测试脚本能否启动。
- `outputs/` 只放训练产物、checkpoint、metrics、history、run summary 和日志；`figures/` 只放报告/PPT 可复用图表。
- `_workflow/` 只放状态追踪文件，不要混入代码、模型或报告资产。
- 若已有实现是平铺结构，且当前任务允许整理，应迁移为该标准布局；如果迁移风险较高，至少在 `implementation_result.notes` 和 `verifier_handoff.risks` 中记录偏离点，并不得把结构混乱的实现标为完全就绪。

## 文件范围

允许修改：

- `code/workN code/` 下与当前实验直接相关的源码、脚本、测试、README、依赖文件和输出目录约定。
- `_workflow/` 下由 `experiment-state-tracker` 管理的状态文件。

不得修改：

- 其他实验的 `code/workM code/`
- 实验要求 PDF
- 报告模板原始文件，除非后续 report writer 明确需要
- PPT 生成工具
- 与当前实验无关的全局配置

如果必须新增依赖：

- 优先选择课程实验常用且必要的依赖。
- 更新 `requirements.txt` 或 README。
- 在 `verifier_handoff.risks` 中说明新增依赖可能带来的环境风险。

## 最低实现内容

如果从零实现，通常至少准备：

- `README.md`：说明环境检查、测试、训练、评估命令。
- `requirements.txt`：列出必要依赖。
- `check_environment.py`：检查关键依赖和设备状态，若已有通用检查可复用。
- 数据准备/检查入口：如 `prepare_data_*.py` 或 `check_data_*.py`，用于训练前确认真实数据已就绪。
- 训练入口：如 `train_*.py`。
- 评估入口：如 `evaluate_*.py`。
- 包目录：模型、数据、训练工具、评估指标和通用工具等模块；从零实现时不得只创建根目录级 `model.py`、`data.py`、`train.py`、`evaluate.py` 平铺结构。
- `tests/`：覆盖模型前向、数据形状、训练/评估关键函数的轻量测试。
- `outputs/`：作为训练产物和指标文件默认目录。
- `figures/`：作为训练曲线、混淆矩阵、结构图等报告/PPT 资产默认目录。
- `data/`：作为该实验真实训练/评估数据目录；不要把数据散放在工作区根目录。

如果修复已有实现，至少保证：

- 缺失或错误逻辑已对照要求修正。
- 入口命令仍清晰可运行。
- 测试或 smoke test 能覆盖本次关键修改。
- README 与实际命令一致。

## 轻量 sanity check

实现器可以运行轻量命令，例如：

- Python 语法检查
- 单个模型前向 shape 检查
- 不下载真实数据的 synthetic smoke test
- 真实数据目录结构检查（不启动训练）
- 小规模单元测试

规则：

- 运行过的 sanity command 必须写入 `_workflow/execution_log.md`。
- sanity check 失败时，应修复后再交给 verifier；如果无法修复，输出 `status: blocked`。
- sanity check 通过不等于实验验证通过，不得写成“指标达标”。

## 状态追踪交接

实现完成后，使用 `skills/experiment-state-tracker/SKILL.md` 更新：

- `_workflow/workflow_state.yaml` 中的 `implementation`
- `_workflow/artifacts_manifest.yaml` 中新增或修改的源码、测试、README、依赖文件
- `_workflow/artifacts_manifest.yaml` 中数据准备脚本、本地/外部数据来源记录、数据检查日志
- `_workflow/execution_log.md` 中本阶段运行过的 sanity command
- `_workflow/workflow_state.yaml` 中仍未覆盖的 requirement、风险和阻塞项

实现器应把 `verifier_handoff.recommended_commands` 写清楚，供 `experiment-verifier` 直接执行。

## 失败处理

- 如果要求、代码目录或状态文件冲突，返回 `needs_clarification` 或 `blocked`，不要继续写代码。
- 如果环境结论是 `not_ready`，不要实现依赖不可用环境才能检查的复杂路径；先报告阻塞或只做不依赖运行环境的静态修改。
- 如果现有代码状态混乱，先做小范围修复和最小可验证入口，不要大规模重构。
- 如果硬性要求无法由现有资源满足，应记录原因，并把对应 requirement 标记为 `pending` 或 `blocked`。

## 边界

这个 skill 不得：

- 宣称最终测试通过、训练完成或指标达标
- 虚构 accuracy、loss、BLEU、困惑度等实验指标
- 生成最终实验报告或 PPT
- 修改其他实验工作区
- 隐藏未实现要求或失败的 sanity check
- 删除历史日志、checkpoint 或用户已有文件来制造“干净状态”
