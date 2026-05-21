---
name: experiment-environment-checker
description: 在实验实现与训练前检查本地运行环境是否可用。适用于已经确定 `code_dir` 或目标代码工作区后，需要核验 Conda、Python、PyTorch、CUDA、依赖状态，并给出推荐解释器、推荐命令前缀和环境结论的场景。
---

# 实验环境核验器

## 概述

在实验实现、测试、训练和评估之前使用这个 skill。
它只负责核验本地运行环境是否满足实验执行要求，并输出结构化环境结论，供后续阶段使用。

如果 `code_dir` 已存在，则优先结合代码目录中的环境检查脚本、依赖文件和 README。
如果 `code_dir` 还不存在，这个 skill 仍然应完成系统级环境核验，而不是报错退出。

不要用这个 skill 去分析代码结构、制定实现方案、修改代码、运行正式训练，或撰写报告。

## 输入

- `code_dir`
- `code_dir_state`
- 可选的 `requirement_summary`

## 输出

返回一个结构化结果，格式如下：

```yaml
runtime_profile:
  python_executable:
  python_version:
  conda_env:
  user_site_enabled:
  torch_version:
  torchvision_version:
  cuda_available:
  cuda_version:
  package_summary: []
recommended_command_prefix:
environment_status:
issues: []
commands_run: []
notes:
```

允许的 `environment_status` 值：

- `ready`
- `partial`
- `not_ready`
- `unknown`

## 核验流程

1. 先确认当前任务的 `code_dir` 和 `code_dir_state`。
2. 检查本机是否存在可用的 Conda / Python 解释器。
3. 检查 Python 版本是否符合当前项目预期。
4. 检查 PyTorch 与 torchvision 是否可导入。
5. 检查 CUDA 是否可用，以及 CUDA 版本信息。
6. 如果代码目录中存在 `check_environment.py`，优先运行它并纳入结论。
7. 如果代码目录中存在 `requirements.txt`，对关键依赖进行核对。
8. 如果 Phase 2 已识别本地伴随数据资产，只确认路径可访问并记录事实；不解压、不下载、不运行正式训练。
9. 输出推荐解释器和推荐命令前缀。

## 核验建议

- 在当前项目中，优先检查 Conda 环境 `python_cuda` 与 Python `3.12.12`。
- 如果怀疑 `AppData\\Roaming` 下的 user-site 包覆盖了 Conda 环境，优先考虑使用 `-s` 禁用 user-site。
- 如果代码目录中已经提供 `check_environment.py`，优先复用现有检查逻辑，而不是重复发明一套检测方式。
- 如果 `code_dir_state` 为 `to_create`，则环境核验只做系统级检查，不要求代码目录内文件必须存在。
- 不要把环境核验和代码基线检查混在一起；这个 skill 只输出环境结论，不解释代码状态。
- 数据集是否已经可用于训练不由本阶段最终判定；本阶段最多记录本地资产是否可见，正式数据准备与数据就绪检查必须在后续阶段完成。

## 字段规则

- `runtime_profile.python_executable`：推荐使用的解释器路径
- `runtime_profile.python_version`：实际检测到的 Python 版本
- `runtime_profile.conda_env`：检测到的 Conda 环境名称；未知时可留空或备注
- `runtime_profile.user_site_enabled`：user-site 是否启用
- `runtime_profile.torch_version`：检测到的 torch 版本；不可用时注明
- `runtime_profile.torchvision_version`：检测到的 torchvision 版本；不可用时注明
- `runtime_profile.cuda_available`：`true` / `false`
- `runtime_profile.cuda_version`：检测到的 CUDA 版本；未知时注明
- `runtime_profile.package_summary`：关键依赖的状态摘要
- `recommended_command_prefix`：后续运行训练、测试、评估时推荐沿用的命令前缀
- `issues`：阻塞项、风险项、异常项
- `commands_run`：本阶段实际执行过且影响环境结论的检查命令摘要
- `notes`：其他有用但非阻塞的信息
- 如果环境检查输出较长或会支撑报告结论，应保存为日志文件并登记为 `environment_log`

## 输出规则

- 结果必须紧凑、结构化、可直接被后续阶段复用。
- 优先输出环境事实，不要夹带实现建议。
- 如果环境基本可用但有风险项，使用 `partial`，并把问题写入 `issues`。
- 只有在关键运行条件满足时，才使用 `ready`。
- 如果信息不足但尚未完全失败，使用 `unknown` 或 `partial`，不要伪造结论。
- 环境检查命令、关键输出和环境日志应交给 `experiment-state-tracker` 写入执行日志和产物清单。
- 后续训练、测试、评估命令应复用 `recommended_command_prefix`，避免不同解释器造成结果不可复现。

## 状态追踪交接

环境核验完成后，使用 `skills/experiment-state-tracker/SKILL.md` 更新：

- `_workflow/workflow_state.yaml` 中的 `runtime_profile`
- `_workflow/execution_log.md` 中的环境检查命令
- `_workflow/artifacts_manifest.yaml` 中的环境日志或检查脚本

如果环境未就绪，应把阻塞项写入状态文件的 `open_issues`，不得继续伪装成可训练状态。

## 失败处理

- 如果 Python 或关键依赖无法导入，返回 `not_ready`。
- 如果 CUDA 不可用但实验明显依赖 GPU，可返回 `partial` 或 `not_ready`，并明确写入 `issues`。
- 如果存在多个解释器冲突，优先给出推荐解释器，并在 `issues` 中记录冲突情况。
- 如果无法检测到足够信息形成结论，返回 `unknown`。

## 边界

这个 skill 不得：

- 分析代码结构或判断代码质量
- 选择最终算法方案
- 创建或修改代码文件
- 运行正式训练、评估或单元测试
- 生成实验报告或 PPT
