---
name: experiment-requirement-reader
description: 读取国科大实验要求 PDF 和同目录伴随数据资产，并在任何实现工作开始前提取结构化实验摘要。适用于实验 PDF 已经定位完成，下一步需要识别实验目标、必做任务、硬性指标、提交物、数据集来源、理论范围，以及 PDF 中示例代码说明的场景。
---

# 实验要求解析器

## 概述

在实验 PDF 已经定位完成后使用这个 skill。
它只负责读取 PDF、枚举同目录伴随数据资产，并把内容转换成紧凑、结构化的实验要求摘要，供后续实现、数据准备、验证和报告撰写阶段使用。

不要用这个 skill 去设计算法、判断环境是否就绪、修改代码、运行测试，或直接写报告。

## 输入

- `pdf_path`
- `requirement_dir`
- `companion_files`
- 可选的 `experiment_id`
- 来自路由阶段的可选 `experiment_name`

## 输出

返回一个结构化结果，格式如下：

```yaml
experiment_id:
experiment_name:
requirement_summary:
  objectives: []
  required_tasks: []
  hard_constraints: []
  theory_scope: []
target_metrics: []
deliverables: []
provided_assets: []
dataset_requirements:
  name:
  source_type:
  required_files: []
  local_assets: []
  external_source_needed:
  notes: []
requirement_evidence: []
sample_code_notes:
  present:
  notes: []
ambiguities: []
status:
notes:
```

允许的 `status` 值：

- `complete`
- `partial`
- `unreadable`
- `needs_clarification`

## 阅读流程

1. 先使用最快且可靠的本地文本提取方法读取 PDF。
2. 如果工具支持分页输出，优先保留页码；如果只能获得整篇文本，应在 `ambiguities` 说明页码不可确定。
3. 识别真正影响执行的章节，重点包括：
   - 实验标题
   - 实验目的
   - 实验要求
   - 目标指标
   - 提交物要求
   - 数据集名称、文件格式、是否随实验要求提供、是否允许/需要外部下载
   - 理论或原理部分
   - 示例代码或实现提示
4. 将严格要求和背景说明分开。
5. 只提取 PDF 中明确写出的信息。
6. 对缺失项或歧义项进行记录，而不是猜测补全。

## 提取建议

- 优先文本提取，再考虑逐页人工阅读。
- 在当前项目中，如果可用，`pdftotext -enc UTF-8 -layout` 是一个很好的第一选择。
- 如果文本提取质量较差，则直接检查关键页面，并只恢复需要的部分。
- 除非 PDF 明确要求详细推导，否则公式和背景原理只需简要提炼。
- 对准确率、时间要求、提交要求等数值门槛必须原样保留。

## 字段规则

- `requirement_summary.objectives`：实验希望掌握、理解或展示的内容
- `requirement_summary.required_tasks`：实现阶段必须完成的具体任务
- `requirement_summary.hard_constraints`：绝对不能忽略的硬性要求
- `requirement_summary.theory_scope`：后续实验报告应解释的理论范围
- `target_metrics`：PDF 中明确写出的可测量目标
- `deliverables`：PDF 中明确要求提交的材料
- `provided_assets`：`requirement_dir` 中除 PDF 以外的伴随文件清单，需标注是否为数据资产、参考资料、示例代码或其他材料
- `dataset_requirements.name`：实验使用的数据集或数据文件名称；PDF 未写明时记录 `unknown`
- `dataset_requirements.source_type`：`provided_local`、`standard_library`、`external_open_source`、`unspecified` 之一
- `dataset_requirements.required_files`：PDF 明确要求的文件名、压缩包、目录或数据格式
- `dataset_requirements.local_assets`：`companion_files` 中和当前实验相关的本地数据资产；如实验三的 `tang.npz.zip.zip`
- `dataset_requirements.external_source_needed`：本地无数据且 PDF 未提供标准库可直接获取数据时为 `true`
- `dataset_requirements.notes`：数据规模、类别、字段、预处理要求、下载限制等
- `requirement_evidence`：关键要求的来源信息，尽量包含页码、章节和短摘
- `sample_code_notes.present`：`true` 或 `false`
- `sample_code_notes.notes`：是否存在示例代码、它的作用，以及后续阶段需要重点验证的点
- `ambiguities`：未解决要求、表述不清之处或 PDF 中缺失的重要信息

## 输出规则

- 结果必须紧凑、结构化。
- 优先使用列表，而不是长篇散文。
- 不要把实现建议混入要求提取结果中。
- 不得默默推断 PDF 中未写出的指标或提交物。
- 如果某字段缺失，使用空列表或简短备注，不得编造内容。
- 关键硬性约束、指标和提交物应能交给 `experiment-state-tracker` 建立稳定 requirement ID。
- 如果 `companion_files` 中存在数据资产，应优先记录为本地提供数据，不要建议绕过本地文件另行下载。
- 如果 PDF 指向标准公共数据集但本地没有数据文件，记录清楚推荐来源类型；真正联网确认外部开源来源留给实现/验证阶段，并必须登记来源。
- 如果无法确认页码或章节，应在 `ambiguities` 中说明，不要假装来源明确；后续报告不得把 `page: unknown` 写成确定来源。

## 状态追踪交接

解析完成后，使用 `skills/experiment-state-tracker/SKILL.md` 将以下内容写入对应实验的 `_workflow/workflow_state.yaml`：

- `requirement_summary`
- `target_metrics`
- `deliverables`
- `provided_assets`
- `dataset_requirements`
- `requirement_evidence`
- `ambiguities`

硬性指标、硬性约束和提交物必须成为可追踪条目，供后续实现、验证和报告引用。
数据集要求和本地伴随资产必须写入状态文件，供后续数据准备和训练前核验引用。

## 失败处理

- 如果 PDF 完全无法读取，返回 `status: unreadable`。
- 如果 PDF 可以读取，但关键要求仍不清晰，返回 `status: needs_clarification` 或 `partial`。
- 如果部分提取结果仍然有价值，则提供所有已确认字段，并把未知项列入 `ambiguities`。

## 边界

这个 skill 不得：

- 选择最终实现方案
- 通过执行验证示例代码
- 检查 Conda、Python、PyTorch 或 CUDA
- 创建或修改代码文件
- 运行训练或评估
- 生成实验报告或 PPT
