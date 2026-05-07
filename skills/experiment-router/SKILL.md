---
name: experiment-router
description: 在任何 PDF 阅读或代码工作开始前，将用户请求路由到正确的国科大实验。适用于“完成实验X”“做第X个实验”或提到实验编号、实验名称的请求，用于把一次请求匹配到 `实验要求（来自国科大在线）/` 下唯一的实验要求子目录、实验 PDF、伴随数据资产，以及该实验专属的目标代码工作区 `code/workN code/`。
---

# 实验路由器

## 概述

在实验任务的最开始使用这个 skill。
它只负责把用户请求映射到唯一实验、唯一要求子目录、唯一 PDF、同目录伴随数据资产和该实验专属的目标代码工作区。

目标代码工作区可能已经存在，也可能需要在后续阶段创建。
如果当前没有现成代码目录，这本身不是错误。

不要用这个 skill 去深读 PDF、分析实现细节、修改代码、运行测试，或撰写报告。

## 输入

- 用户请求文本
- `实验要求（来自国科大在线）/`
- `code/` 下现有的 `work* code/` 目录

## 输出

返回一个紧凑的路由结果，结构如下：

```yaml
experiment_id:
experiment_name:
requirement_dir:
pdf_path:
companion_files: []
code_dir:
code_dir_state:
status:
notes:
```

允许的 `status` 值：

- `matched`
- `ambiguous`
- `missing_pdf`

允许的 `code_dir_state` 值：

- `existing`
- `to_create`

## 路由流程

1. 从用户请求中提取实验编号、实验名称和其他稳定关键词。
2. 在 `实验要求（来自国科大在线）/` 中递归搜索候选要求子目录和 PDF。
3. 在项目根目录的 `code/` 子目录中搜索现有候选工作区，例如 `code/work1 code/`。
4. 优先按精确实验编号匹配。
5. 如果编号不足以确定，再按共享实验标题关键词匹配。
6. 优先选择唯一的高置信度 PDF 匹配结果。
7. 对最终候选 `pdf_path` 执行存在性确认；如果文件名推导出的路径不存在，必须回到目录列表重新匹配真实文件名。
8. 将 `pdf_path` 的父目录记为 `requirement_dir`，枚举该目录下非 PDF 的伴随文件到 `companion_files`。
9. 如果该实验专属代码工作区已经存在，则直接复用。
10. 如果该实验专属代码工作区不存在，则推导目标路径为 `code/workN code/`，其中 `N` 为路由出的实验编号。
11. 如果实验匹配结果不唯一，则停止并报告歧义，而不是猜测。

## 匹配规则

- 精确实验编号匹配优先级最高。
- 精确共享标题关键词匹配优先级次之。
- 弱模糊匹配只能作为候选提示，不能作为最终依据。
- 实验 PDF 是必需项。
- `pdf_path` 必须是实际存在的文件路径，不得写入推测路径或规范化后的伪路径。
- `requirement_dir` 必须是实际存在的目录。
- `companion_files` 只列出与该实验同目录的非 PDF 文件，例如 `.zip`、`.npz`、`.csv`、`.txt`、`.json`、`.tar` 等；没有则为空列表。
- 代码工作区在路由阶段不是必需项。
- 如果 PDF 已匹配但没有现成代码工作区，应返回 `code_dir_state: to_create`。
- 目标工作区必须位于 `code/` 下，且目录名称严格遵循真实实验编号，例如 `code/work1 code/`、`code/work2 code/`。
- 一个实验必须且只能对应 `code/` 下一个独立代码工作区。
- 不允许多个实验共用同一个 `code/workN code/`。
- 不允许把实验 X 路由到实验 Y 的代码目录。

## 搜索建议

- 优先使用快速本地搜索工具，如 `rg` 或目录枚举。
- 重点查找 `实验1`、`实验 1`、`work1`、`experiment 1` 以及标题关键词。
- PDF 可能位于 `实验N要求/` 子目录内，不要只搜索要求根目录第一层。
- 先利用文件名和目录名判断，再决定是否深入打开文件。
- 只有在命名不足以区分时，才打开文件进一步确认。
- 在 Windows 上注意中文全角符号、`+`、`：` 等文件名差异；状态文件中必须写真实文件名。

## 交接规则

如果 `status: matched`，则向下一阶段交接以下字段：

- `experiment_id`
- `experiment_name`
- `requirement_dir`
- `pdf_path`
- `companion_files`
- `code_dir`
- `code_dir_state`

随后使用 `skills/experiment-state-tracker/SKILL.md` 初始化或更新：

- `code/workN code/_workflow/workflow_state.yaml`
- `code/workN code/_workflow/artifacts_manifest.yaml`
- `code/workN code/_workflow/execution_log.md`

如果 `code_dir_state: to_create`，状态追踪阶段可以在唯一匹配后创建 `code/workN code/` 和 `_workflow/`；路由器本身仍不得创建文件或目录。

如果结果不是 `matched`：

- 如果用户可以消除歧义，只提一个简洁澄清问题。
- 否则准确说明缺失项或冲突点。

## 边界

这个 skill 不得：

- 读取完整实验 PDF 并提取内容
- 决定最终实现方案
- 创建文件或目录
- 修改代码
- 运行测试或训练
- 生成实验报告或 PPT
