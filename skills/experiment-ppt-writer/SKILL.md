---
name: experiment-ppt-writer
description: 基于已验证的深度学习实验报告、指标、图表和 `_workflow` 证据链生成实验汇报 PPT。适用于 Phase 8 的强制最终交付阶段；当实验代码、验证和报告已经完成后，需要把 `workflow_state.yaml`、`artifacts_manifest.yaml`、`execution_log.md` 和报告产物整理成 ppt-master 可消费的演示简报，并调用 `PPT生成skill/skills/ppt-master/SKILL.md` 完成 PPTX 输出的场景。
---

# 实验 PPT 撰写器

## 概述

在实验报告完成后作为 Phase 8 必做收尾阶段使用这个 skill。
它负责把实验事实整理成 PPT 简报输入，并把生成出的 PPT 文件登记回 `_workflow`；具体 SVG 页面生成和 PPTX 导出交给 `PPT生成skill/skills/ppt-master/SKILL.md`。

不要用这个 skill 绕过报告、验证或 ppt-master 的强制流程。
不要把 PPT 视为可选项；完整实验任务必须在本阶段完成后才可交付。

## 前置条件

进入 PPT 阶段前必须确认：

- `workflow_state.yaml`、`artifacts_manifest.yaml`、`execution_log.md` 均存在。
- `verification.overall_passed == true`，或未达标/阻塞项已经在 `open_issues` 中如实记录。
- `phase7_report.status == completed`。
- 报告 `.tex` 和 `.pdf` 已登记到 manifest，且文件实际存在。
- `data_readiness` 已登记，PPT 中的数据集描述必须和训练前数据检查记录一致。
- PPT 将引用的指标、图片、表格、代码片段均能追溯到 requirement、command 或 artifact。

如果任一条件不满足，返回 `blocked`，不要先做 PPT。

## 输入

- `code/workN code/_workflow/workflow_state.yaml`
- `code/workN code/_workflow/artifacts_manifest.yaml`
- `code/workN code/_workflow/execution_log.md`
- 已完成的报告 `.tex` 和 `.pdf`
- 已登记的图表、指标文件和关键源码文件
- `PPT生成skill/CLAUDE.md`
- `PPT生成skill/skills/ppt-master/SKILL.md`

## 输出

返回结构化结果：

```yaml
ppt_result:
  status:
  project_path:
  brief_path:
  pptx_path:
  slide_count:
  evidence_coverage:
    all_slides_traced: true | false
    untraced_slides: []
  commands_run: []
  notes:
```

允许的 `status` 值：

- `completed`
- `partial`
- `blocked`
- `needs_clarification`

---

## PPT 风格规范

### 配色方案

| 用途 | 颜色名称 | HEX 值 | 说明 |
|------|---------|--------|------|
| 主导色 | 学术蓝 | `#1A5F9E` | 标题栏、重点标记 |
| 辅助色 | 深灰 | `#2D3748` | 正文主色 |
| 强调色 | 橙色 | `#E07C24` | 关键数字、达标标记 |
| 背景色 | 浅灰白 | `#F7F9FC` | 页面背景 |
| 卡片背景 | 白色 | `#FFFFFF` | 内容卡片 |
| 边框色 | 浅灰 | `#E2E8F0` | 卡片边框、分割线 |
| 成功色 | 绿色 | `#38A169` | 达标、通过 |
| 警告色 | 红色 | `#E53E3E` | 未达标、注意 |

### 字体规范

- **中文**：Microsoft YaHei, PingFang SC, sans-serif
- **英文/数字**：Segoe UI, Arial, Helvetica, sans-serif
- **代码**：Consolas, Monaco, monospace

### 字号层级

| 层级 | 用途 | 字号 | 字重 |
|------|------|------|------|
| H1 | 封面标题 | 48px | bold |
| H2 | 章节标题/页标题 | 32px | bold |
| H3 | 卡片标题 | 24px | bold |
| Body | 正文内容 | 18px | normal |
| Small | 辅助说明 | 14px | normal |
| Caption | 脚注/页码/参考文献 | 12px | normal |

### 布局参数

- **Canvas**：1280×720（viewBox `0 0 1280 720`，16:9）
- **边距**：60px（左右）、50px（上下）
- **内容区域**：1160×620
- **卡片间距**：24px
- **卡片圆角**：8px（rx="8" ry="8"）

### 布局网格

- **单栏布局**：全宽内容展示
- **双栏布局**：左右各 530px，间距 100px
- **三栏布局**：每栏 350px，间距 55px
- **四栏布局**：每栏 260px，间距 40px

### 图标库

统一使用 chunk（fill, straight-line），不混用其他图标风格。

---

## 内容提取规则

### 固定 8 页结构与数据来源

| 页码 | Slide 标题 | 数据来源 | 提取内容 | 参考文献脚注 |
|------|-----------|---------|---------|-------------|
| 1 | 封面 | workflow_state.yaml | 实验名称、课程、日期 | 无 |
| 2 | 实验概述 | 实验要求 PDF + data_readiness + 报告§一 | 目标、数据集来源、评价标准 | 按需标注报告引用 |
| 3 | 理论原理 | 报告§二 | 核心公式（交叉熵、卷积、ReLU）、CNN 原理 | 按需标注报告引用 |
| 4 | 算法设计 | 报告§三 + 源码 | 模型结构图、算法流程图、关键代码片段 | 无 |
| 5 | 实验设置 | workflow_state.yaml + execution_log.md | 环境、超参数、优化器配置 | 按需标注报告引用 |
| 6 | 实验结果 | metrics JSON + 报告§四 | 逐轮指标表格、训练曲线图 | 无 |
| 7 | 结果分析 | 报告§四 + metrics | 混淆矩阵、实际 vs 目标对比、达标判断 | 无 |
| 8 | 总结与展望 | 报告§四末尾段 | 核心结论、收获、改进方向 | 无 |

### 参考文献处理

不设独立参考文献页。每页 PPT 底部使用小字体（10-12px）标注该页引用的参考文献，格式如 `[1] LeCun et al., 1998`。引用编号与实验报告中的 `\cite{key}` 对应。

### 内容精炼原则

- PPT 内容必须比报告更聚焦，不要把报告整段搬进 slide
- 优先使用已经登记的图表、流程图、结构图和训练曲线
- 每页只表达一个主结论，标题应是结论型标题
- 结果页必须包含定量指标和目标对比
- 未达标、限制或阻塞项必须如实呈现，不能做成"已完成"的叙事
- 视觉生成细节遵守 ppt-master，不在本 skill 中复制其 SVG 约束

---

## Slide 结构定义

### Slide 01 - 封面

- **文件名**：`slide_01_cover.svg`
- **布局**：居中对称
- **必需元素**：
  - 实验标题（如"实验一：手写数字识别"）
  - 课程名称（如"深度学习"）
  - 日期
  - 装饰元素：学术蓝色几何图形（矩形/线条）
- **禁止元素**：报告全文摘要、学生个人信息占位

### Slide 02 - 实验概述

- **文件名**：`slide_02_overview.svg`
- **布局**：标题 + 三栏卡片 或 标题 + 左右双栏
- **必需元素**：
  - 实验目标（来自要求 PDF）
  - 数据集描述（来源、规模、格式；来自 `dataset_requirements` 和 `data_readiness`）
  - 评价标准（准确率 >= 98%）
  - 任务完成情况摘要表
- **参考文献脚注**：引用报告中的 MNIST/LeCun 等引用

### Slide 03 - 理论原理

- **文件名**：`slide_03_theory.svg`
- **布局**：标题 + 多行公式卡片
- **必需元素**：
  - 核心公式：卷积、ReLU、交叉熵、AdamW 更新规则
  - 每个公式配一句话说明
  - 使用 SVG text 元素渲染公式（LaTeX 风格排版）
- **参考文献脚注**：引用 Nair & Hinton (ReLU)、Loshchilov & Hutter (AdamW) 等

### Slide 04 - 算法设计

- **文件名**：`slide_04_algorithm.svg`
- **布局**：标题 + 左图右文 或 双栏
- **必需元素**：
  - 模型结构图（嵌入已有 SVG/PNG）
  - 算法流程图（嵌入已有 SVG/PNG）
  - 关键代码片段（简短，< 8 行）
  - 模型架构文本描述
- **禁止元素**：完整源码列表

### Slide 05 - 实验设置

- **文件名**：`slide_05_setup.svg`
- **布局**：标题 + 参数卡片网格
- **必需元素**：
  - 运行环境（Python、PyTorch、CUDA 版本）
  - 超参数表（epochs、batch_size、lr、weight_decay、dropout、seed）
  - 优化器：AdamW
  - 损失函数：CrossEntropyLoss
- **参考文献脚注**：引用 PyTorch、AdamW 等

### Slide 06 - 实验结果

- **文件名**：`slide_06_results.svg`
- **布局**：标题 + 上表下图 或 左表右图
- **必需元素**：
  - 逐轮指标表格（epoch、train_loss、train_acc、test_loss、test_acc）
  - 训练曲线图（嵌入已有 SVG/PNG）
  - 关键数字高亮：最佳准确率 99.28%
- **禁止元素**：原始 JSON 数据

### Slide 07 - 结果分析

- **文件名**：`slide_07_analysis.svg`
- **布局**：标题 + 左图右分析
- **必需元素**：
  - 混淆矩阵图（嵌入已有 SVG/PNG）
  - 目标 vs 实际对比（98% vs 99.28%）
  - 达标判断（使用绿色/成功色）
  - 误差模式简述（如 3↔5、4↔9 混淆）
- **禁止元素**：虚构的消融实验或对比数据

### Slide 08 - 总结与展望

- **文件名**：`slide_08_summary.svg`
- **布局**：标题 + 要点列表 或 双栏
- **必需元素**：
  - 核心结论（一句话）
  - 关键收获（2-3 点）
  - 改进方向（2-3 点）
  - 致谢或结束标记
- **禁止元素**：新引入未验证的结论

---

## PPT Brief 规则

在调用 ppt-master 前，先生成 `ppt_brief.md`，建议保存在：

```text
code/workN code/_workflow/ppt_brief.md
```

也可保存到 `PPT/实验N/ppt_brief.md` 作为独立副本。

`ppt_brief.md` 必须包含：

- 实验标题、课程、实验编号。
- 面向听众与汇报时长。
- 推荐页数（8 页）。
- 每页 slide 的标题、核心信息、证据 ID、可用图表和备注。
- 必须展示的关键指标和达标结论。
- 不得展示的未验证内容。

---

## ppt-master Pipeline 对接

将 skill 与 ppt-master 的 7 步 pipeline 对应如下：

### Step 1: Source（源内容处理）

直接使用 `ppt_brief.md`（从 workflow 数据生成），无需 PDF 转换。

### Step 2: Init（项目初始化）

```bash
python PPT生成skill/skills/ppt-master/scripts/project_manager.py init <experiment_name> --format ppt169
```

项目创建在 `PPT生成skill/projects/<experiment_name>/` 下。

### Step 3: Template（模板选择）

选择"自由设计"（无预置模板），使用本 skill 中定义的风格参数。

### Step 4: Strategist（策略师阶段）

由本 skill 充当 strategist，直接生成 `design_spec.md`。
由于风格参数已在本文档中固定，跳过八确认阻塞步骤。

`design_spec.md` 模板骨架：

```markdown
# 演示文稿设计规范与内容大纲

## 项目信息

- **项目名称**：实验N：{experiment_name}
- **来源文档**：实验报告、workflow_state.yaml、metrics JSON
- **目标受众**：课程教师、助教
- **使用场景**：实验汇报

## 1. 画布格式声明

| 属性 | 值 |
|------|-----|
| 画布尺寸 | 1280×720 |
| 比例 | 16:9 |
| viewBox | 0 0 1280 720 |

## 2. 视觉主题

- 主题类型：亮色主题
- 设计风格：学术汇报风格
- 整体调性：简洁、专业、数据驱动

## 3. 色彩方案

（使用本 skill "配色方案" 章节中的固定参数）

## 4. 排版体系

（使用本 skill "字体规范" 和 "字号层级" 章节中的固定参数）

## 5. 核心布局原则

（使用本 skill "布局参数" 章节中的固定参数）

## 6. 页面序列规划

（使用本 skill "Slide 结构定义" 章节中的固定结构，
 变量部分由实验数据填充：实验名称、slide 内容、图表文件路径）
```

### Step 5: Image Generator（图片生成）

跳过。使用实验已有的真实图表，不用 AI 生图。
将实验图表（SVG/PNG）复制到项目的 `images/` 目录。

### Step 6: Executor（执行器阶段）

按 design_spec 逐页生成 SVG 文件到 `svg_output/` 目录。
每页 SVG 必须遵守 `shared-standards.md` 中的 SVG 约束：
- viewBox: `0 0 1280 720`
- 仅使用内联样式（禁止 `<style>`、`class`）
- 禁止 `mask`、`foreignObject`、`textPath`、`animate`
- 系统字体（Microsoft YaHei、Segoe UI）
- HEX 颜色
- `<image>` 标签引用图表文件

### Step 7: Post-process & Export（后处理与导出）

严格按顺序执行以下三条命令：

```bash
python PPT生成skill/skills/ppt-master/scripts/total_md_split.py --project <project_path>
python PPT生成skill/skills/ppt-master/scripts/finalize_svg.py --project <project_path>
python PPT生成skill/skills/ppt-master/scripts/svg_to_pptx.py --project <project_path> -s final
```

绝不使用 `cp` 替代 `finalize_svg.py`；从 `svg_final/`（而非 `svg_output/`）导出。

---

## 执行流程

1. 读取 `_workflow` 三件套，确认报告与验证状态。
2. 检查报告 PDF、指标文件、图表文件是否存在并在 manifest 中登记。
3. 建立 slide 级证据映射：
   - 每页必须有 `slide_id`。
   - 每页至少关联一个 requirement、metric、command 或 artifact。
   - 结论页必须关联 verifier 指标。
4. 生成 `ppt_brief.md`。
5. 初始化 ppt-master 项目（`project_manager.py init`）。
6. 复制实验图表到项目 `images/` 目录。
7. 生成 `design_spec.md`（使用本 skill 中的模板骨架）。
8. 按 slide 结构定义逐页生成 SVG 文件。
9. 执行后处理三步流程（total_md_split → finalize_svg → svg_to_pptx）。
10. 将最终 PPTX 复制到 `PPT/实验N/` 目录。
11. 将 `pptx_path`、`ppt_brief.md`、关键 SVG 页面和导出命令写回 `_workflow`。

---

## 状态追踪交接

PPT 完成后，使用 `experiment-state-tracker` 更新：

- `workflow_state.yaml` 中的 `ppt` 和 `phase8_ppt`：
  ```yaml
  phase8_ppt:
    status: completed
    updated_at: YYYY-MM-DD
    outputs:
      brief_path: PPT/实验N/ppt_brief.md
      project_path: PPT生成skill/projects/<name>/
      pptx_path: PPT/实验N/实验N PPT.pptx
      slide_count: 8
  ppt:
    brief_path: PPT/实验N/ppt_brief.md
    slides:
      - id: slide-001
        title: 封面
        evidence: []
      - id: slide-002
        title: 实验概述
        evidence: [req-001, req-006]
      # ... 每个 slide
    outputs:
      - PPT/实验N/实验N PPT.pptx
  ```
- `artifacts_manifest.yaml` 中的 `ppt_brief.md`、PPTX、关键 SVG、PPT 项目目录。
- `execution_log.md` 中 ppt-master 的关键命令。

---

## 失败处理

- 报告未完成：返回 `blocked`，要求先完成报告。
- 指标未验证：返回 `blocked`，要求先完成 verifier。
- 图表不足：可返回 `partial`，并建议先使用 `experiment-diagram-maker` 补齐。
- ppt-master 导出失败：记录错误命令和输出，不得声明 PPT 完成。
- SVG 嵌入图表不兼容：使用 PNG fallback（code/workN code/figures/ 下有 PNG 版本）。
- 字体在 SVG 中不可用：使用通用字体（Microsoft YaHei, Segoe UI, Arial）。

## 边界

这个 skill 不得：

- 在报告未完成前生成 PPT。
- 虚构实验指标、结论、图表或运行命令。
- 修改实验源码。
- 绕过 ppt-master 的确认点和后处理流程。
