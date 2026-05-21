---
name: experiment-ppt-writer
description: 基于已验证的深度学习实验报告、指标、图表和 `_workflow` 证据链生成高质量实验汇报 PPT。适用于 Phase 8 的强制最终交付阶段；当实验代码、验证和报告已经完成后，需要把 `workflow_state.yaml`、`artifacts_manifest.yaml`、`execution_log.md` 和报告产物整理成 ppt-master 可消费的演示简报，并调用 `PPT生成skill/skills/ppt-master/SKILL.md` 按实验一最终优化版的绿色紧凑模板、公式拆页、全页利用和严格预览质检标准完成 PPTX 输出的场景。
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
- `PPT生成skill/skills/ppt-master/references/course-experiment-polished-standard.md`

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

必须优先遵守 `PPT生成skill/skills/ppt-master/references/course-experiment-polished-standard.md`。该文件沉淀了实验一最终优化版的模板、公式页、版式密度、文字边界和导出检查要求；生成其他实验 PPT 时不得退回旧的蓝色稀疏学术模板。

### 配色方案

| 用途 | HEX 值 | 说明 |
|------|--------|------|
| 背景色 | `#F8F7F1` | 温暖浅米白背景 |
| 卡片背景 | `#FFFFFC` | 主卡片 |
| 浅色卡片 | `#F1F4EE` | 内嵌说明、完成状态 |
| 主绿色 | `#265B3D` | 标题、主强调、页眉竖条 |
| 公式绿色 | `#125837` | 所有展示公式 |
| 鼠尾草绿 | `#7E9A7C` | 辅助强调 |
| 棕褐色 | `#977C54` | 第三强调色 |
| 公式底色 | `#F5F0E8` | 公式浅底框 |
| 正文色 | `#34332E` | 正文 |
| 辅助文字 | `#77776F` | 副标题、说明、脚注 |
| 边框线 | `#D6DAD0` | 卡片边框、分割线 |

### 字体规范

- 中文页标题：优先使用 `SimSun` 或正式宋体风格。
- 中文正文：`Microsoft YaHei`。
- 正文、标题、标签、参考文献和技术缩写中的可编辑英文字母：必须使用 `Times New Roman` 作为 Latin typeface；混排文本要同时保留中文 `eastAsia` 字体，不能把整段中英文都改成同一种字体。
- 英文编号、页码和紧凑数字标签可使用 `Cascadia Mono` 或等宽字体；若其中出现英文字母，仍优先设置 Latin typeface 为 `Times New Roman`。
- 代码：`Consolas` 或等宽字体，必须放在明确代码块中。
- 从源代码重新生成图表、表格或结构图时，也应尽量把图内英文设置为 `Times New Roman`；无法编辑的既有位图以清晰可读为先，不得为换字体破坏比例或裁剪。
- 不得把一个英文单词或技术 token 拆到两行。`Transformer`、`Embedding`、`Encoder`、`checkpoint`、`train/valid/test`、`simple-examples` 等必须完整留在同一行；如果空间不够，优先扩大文本框、提前在单词前换行、略微调小字号或改写短句。
- 中英文混排正文不得让 `，`、`。`、`；`、`：`、`、`、`,`、`.` 等标点出现在新行行首；如果 PowerPoint 自动换行会形成行首标点，必须提前在更自然的位置手动换行或微调字号/文本框宽度。

### 字号和密度

- 封面标题：30-36 pt，除非碰到右侧装饰图案或页面边界，否则不强制换行。
- 内容页标题：25-31 pt。
- 卡片标题：16-18 pt。
- 普通正文：10.5-13 pt，讨论卡片不得小于 11.5 pt。
- 公式介绍文字：10.5-11 pt，必须可读，不得为了塞入单页而压小。
- 脚注和页码：7.5-9 pt。

### 布局参数

- Canvas：1280×720 SVG 或 13.333×7.5 in PPTX，16:9。
- 所有内容页左上角页眉位置保持一致：左侧竖条、英文眉题、中文标题、副标题的坐标不得逐页漂移。
- 内容区域应尽量占满页面，主体通常覆盖至少 85% 可用宽度和 70% 可用内容高度。
- 底部除参考文献和页码外不得留下大块空白。
- 卡片圆角保持克制，约 8 px；每个卡片顶部使用细强调线。
- 图片、流程图、曲线图和混淆矩阵必须裁掉无效白边后再放置，并保持投影可读。
- 真实实验图片必须按明确的源文件名/路径引用，例如 `algorithm_flow_*.png`、`training_curve_*.svg`、`confusion_matrix_*.svg`；不得从已优化 PPT 中按“第几个图片”抽取复用，因为装饰图会改变图片顺序并导致真实图表被叶子/背景图替换。
- 删除底部 AI 化说明文字时，必须连同其底部说明框、强调线和空文本框一起删除；不得留下空的装饰框。释放出来的高度应优先分配给主图、指标卡片或正文内容。

### 公式展示标准

- 公式多时必须拆页；每页最多放 4 个公式，使用 2×2 公式卡片。
- 每个公式必须配科学、简要的自然语言解释。
- 公式必须使用标准 LaTeX/Office 公式渲染，颜色统一为 `#125837`。
- 不得出现 `报告公式：`、`AI生成`、`prompt`、内部证据编号、本地路径或工具痕迹。
- 如果标准 LaTeX 无法使用，允许使用裁净白边的公式截图，但截图不得与解释文字重叠。

---

## 内容提取规则

### 页数自适应结构与数据来源

页数不是硬性要求，质量优先于页数压缩。默认可从 10 页基础结构出发，但只要理论公式、流程图、模型结构图、训练曲线、结果样例或讨论内容放在一页会导致文字过小、图片变成缩略图、拥挤或重叠，就必须拆页。实验一最终优化版采用 11 页，其中理论基础拆成两页、每页 4 个公式；其他实验可以根据公式和图表数量继续扩展到 12 页、13 页或更多。页码总数必须按最终页数统一更新。

| 页码 | Slide 标题 | 数据来源 | 提取内容 | 参考文献脚注 |
|------|-----------|---------|---------|-------------|
| 1 | 封面 | workflow_state.yaml | 实验名称、课程、日期 | 无 |
| 2 | 实验概述 | 实验要求 PDF + data_readiness + 报告§一 | 目标、数据集来源、评价标准 | 按需标注报告引用 |
| 3-N | 理论基础 | 报告§二 | 标准 LaTeX 公式、科学解释、核心原理；每页最多 4 个公式 | 按需标注报告引用 |
| N+1 | 算法设计 | 报告§三 + 源码 | 模型结构图、算法流程图、关键代码片段 | 无 |
| N+2 | 实验设置 | workflow_state.yaml + execution_log.md | 环境、超参数、优化器配置 | 按需标注报告引用 |
| N+3 | 实验结果 | metrics JSON + 报告§四 | 逐轮指标表格、训练曲线图 | 无 |
| N+4... | 补充图表/结果证据 | 报告§三/§四 + 图表产物 | 模型结构、训练曲线、指标表、样例预测等；重要图片必须足够大 | 按需 |
| M+1 | 结果分析 | 报告§四 + metrics | 混淆矩阵、实际 vs 目标对比、达标判断 | 无 |
| M+2 | 讨论与展望 | 报告§五 | 局限性、应用方向、未来研究；内容应来自报告讨论部分，不能临时拼接无关材料 | 无 |
| M+3 | 总结 | 报告§五 + 验证指标 | 核心结论、结果证据、主要收获；内容优先来自实验总结，不得包含“感谢聆听”等结束语 | 无 |
| M+4 | 感谢页 | 汇报信息 | 独立结束页，只放实验标题、感谢聆听、批评指正等结束信息 | 无 |

### 参考文献处理

不设独立参考文献页。每页 PPT 底部使用小字体（10-12px）标注该页引用的参考文献，格式如 `[1] LeCun et al., 1998`。引用编号与实验报告中的 `\cite{key}` 对应。

### 内容精炼原则

- PPT 内容必须比报告更聚焦，不要把报告整段搬进 slide
- 优先使用已经登记的图表、流程图、结构图和训练曲线
- 每页只表达一个主结论，标题应是结论型标题
- 结果页必须包含定量指标和目标对比
- 未达标、限制或阻塞项必须如实呈现，不能做成"已完成"的叙事
- 视觉生成细节遵守 ppt-master，不在本 skill 中复制其 SVG 约束
- 面向听众的 PPT 文本必须干净专业，不得出现内部证据编号、本地路径、JSON 文件名、prompt/AI 生成说明或工具痕迹，例如 `证据：`、`req-001`、`metric-001`、`met-001`、`cmd-*`、`execution_log`、`outputs/`、`results/`。这些只允许留在 `_workflow` 追踪文件中，不得进入 `ppt_brief.md` 的可见内容、`design_spec.md` 页面文案、SVG 或 PPT。

---

## Slide 结构定义

下面的页码是内容顺序，不是固定总页数。`N` 表示理论基础最后一页，`M` 表示补充图表/结果证据最后一页；如果理论公式、流程图、模型结构图、训练曲线、指标表或样例预测需要拆页，后续页码和 `slide_{NN}_*.svg` 文件名必须按最终顺序顺延。

### Slide 01 - 封面

- **文件名**：`slide_01_cover.svg`
- **布局**：居中对称
- **必需元素**：
  - 实验标题（如"实验一：手写数字识别"）
  - 课程名称（如"深度学习"）
  - 日期
  - 装饰元素：浅绿色植物线稿或模板同源弱装饰
- **排版要求**：标题能不换行就不换行；只有碰到右侧装饰图案或页面边界时才允许换行
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

### Slide 03-N - 理论基础

- **文件名**：从 `slide_03_theory.svg` 起顺延；多页时使用 `slide_{NN}_theory.svg`
- **布局**：标题 + 2×2 公式卡片；每页最多 4 个公式
- **必需元素**：
  - 报告中的核心公式：归一化、卷积、ReLU、最大池化、Softmax、交叉熵、准确率、AdamW 等，按实验实际内容取舍
  - 每个公式配科学、简要的自然语言说明
  - 使用标准 LaTeX 公式渲染为 SVG/Office 公式，例如 `\frac{}`、`\sqrt{}`、`\sigma`、`\sum`、`\odot`、上下标等必须规范；不得直接展示 `sqrt()`、`sigma()`、`sum()`、`QK^T` 或 ASCII `*` 乘号。
- **禁止元素**：`报告公式：`、公式截图白边、公式与解释文字重叠、单页硬塞超过 4 个公式
- **参考文献脚注**：引用 Nair & Hinton (ReLU)、Loshchilov & Hutter (AdamW) 等

### Slide N+1 - 算法设计

- **文件名**：`slide_{NN}_algorithm.svg`
- **布局**：标题 + 左图右文 或 双栏
- **必需元素**：
  - 模型结构图（嵌入已有 SVG/PNG）
  - 算法流程图（嵌入已有 SVG/PNG）
  - 关键代码片段（简短，< 8 行）
  - 模型架构文本描述
- **图表尺寸要求**：模型结构图或流程图必须作为主视觉之一，宽度不得低于 30% 画布、 高度不得低于 24% 画布；如果图内节点文字偏小，优先左右排版或单独拆成一页，不要缩成小图。
- **禁止元素**：完整源码列表

### Slide N+2 - 实验设置

- **文件名**：`slide_{NN}_setup.svg`
- **布局**：标题 + 参数卡片网格
- **必需元素**：
  - 运行环境（Python、PyTorch、CUDA 版本）
  - 超参数表（epochs、batch_size、lr、weight_decay、dropout、seed）
  - 优化器：AdamW
  - 损失函数：CrossEntropyLoss
- **参考文献脚注**：引用 PyTorch、AdamW 等

### Slide N+3 - 实验结果

- **文件名**：`slide_{NN}_results.svg`
- **布局**：标题 + 上表下图 或 左表右图
- **必需元素**：
  - 逐轮指标表格（epoch、train_loss、train_acc、test_loss、test_acc）
  - 训练曲线图（嵌入已有 SVG/PNG）
  - 关键数字高亮：最佳准确率 99.28%
- **图表尺寸要求**：训练曲线或结果总览图必须可读；宽图应使用接近全宽的横向容器，多个曲线图并列时每张图宽度不得低于 30% 画布。
- **禁止元素**：原始 JSON 数据

### Slide N+4...M - 补充图表与结果证据

- **文件名**：`slide_{NN}_supporting_figure.svg`
- **布局**：标题 + 单张大图，或两张同等重要图的宽松并排布局
- **必需元素**：
  - 模型结构图、指标表、样例预测、混淆矩阵、补充训练曲线等在结果页无法充分展示的重要图表
  - 简短说明该图与实验结论的关系
- **图表尺寸要求**：不要把第二张重要图片压成页脚缩略图；单图页应接近全宽展示并裁掉无效白边。若一页并排后任一图过小，继续拆成下一页。
- **禁止元素**：内部证据 ID、本地路径、原始 JSON/日志文件名

### Slide M+1 - 结果分析

- **文件名**：`slide_{NN}_analysis.svg`
- **布局**：标题 + 左图右分析
- **必需元素**：
  - 混淆矩阵图（嵌入已有 SVG/PNG）
  - 目标 vs 实际对比（98% vs 99.28%）
  - 达标判断（使用绿色/成功色）
  - 误差模式简述（如 3↔5、4↔9 混淆）
- **图表尺寸要求**：分析图表必须大到能在投影上读清坐标、图例和节点文字；如一页放不下，应减少文字或改成左右双栏，不得把图压缩到页脚区域。
- **禁止元素**：虚构的消融实验或对比数据

### Slide M+2 - 讨论与展望

- **文件名**：`slide_{NN}_discussion.svg`
- **布局**：标题 + 三栏卡片
- **必需元素**：
  - 局限性与优化空间
  - 应用方向
  - 未来研究方向
- **写作标准**：模仿顶会/顶刊实验讨论段的克制风格，清楚说明边界条件、应用外延和下一步研究，不要塞入与本实验无关的泛泛口号。
- **禁止元素**：临时强加的无用扩展、未验证的指标、新引入未在报告出现的结论

### Slide M+3 - 总结

- **文件名**：`slide_{NN}_summary.svg`
- **布局**：标题 + 3 条关键结论
- **必需元素**：
  - 实验目标是否完成
  - 最关键的定量结果或达标证据
  - 方法与工程收获
- **禁止元素**：感谢聆听、谢谢、敬请批评指正等结束语

### Slide M+4 - 感谢页

- **文件名**：`slide_{NN}_thanks.svg`
- **布局**：独立结束页
- **必需元素**：
  - 实验标题
  - “感谢聆听！”或同等正式结束语
  - “敬请老师和同学批评指正”等简短说明
- **禁止元素**：新增实验内容、指标、长段总结

---

## PPT Brief 规则

在调用 ppt-master 前，先生成 `ppt_brief.md`，建议保存在：

```text
code/workN code/_workflow/ppt_brief.md
```

不要把 `ppt_brief.md` 留在 `PPT/实验N/`；该目录最终只保留最终交付 PPTX，若课程或用户明确需要 SVG 参考版，才额外保留一个 `_svg.pptx`。旧版、细节修正版、中间导出版必须清理。

`ppt_brief.md` 必须包含：

- 实验标题、课程、实验编号。
- 面向听众与汇报时长。
- 推荐页数（质量自适应；不得把 10 页作为硬性上限，公式或图表较多时必须拆页）。
- 每页 slide 的标题、核心信息、可用图表和面向听众的备注。
- 必须展示的关键指标和达标结论。
- 不得展示的未验证内容。

`ppt_brief.md` 是给 ppt-master 消费的公开内容简报，必须避免任何会被误放到页面上的内部痕迹。若需要保留证据链，另写 `ppt_traceability.md` 或仅更新 `_workflow/workflow_state.yaml`，不要把证据 ID 放进 `ppt_brief.md` 的 slide 文案中。

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
生成 `design_spec.md` 前必须读取 `PPT生成skill/skills/ppt-master/references/course-experiment-polished-standard.md`，并把其中的版式、公式页和检查要求写入设计约束。

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
- 设计风格：实验一最终优化版绿色紧凑学术模板
- 整体调性：温暖、克制、专业、数据驱动、页面利用充分

## 3. 色彩方案

（使用本 skill "配色方案" 章节中的固定参数）

## 4. 排版体系

（使用本 skill "字体规范" 和 "字号层级" 章节中的固定参数）

## 5. 核心布局原则

（使用本 skill "布局参数" 章节中的固定参数）

- 普通内容页应充分利用页面，主体内容覆盖至少 85% 可用宽度和 70% 可用内容高度。
- 重要图表、截图、流程图、架构图和实验结果图必须保证展示可读，默认至少占 30% 画布宽度和 24% 画布高度。
- 若上下堆叠导致图片过小，必须切换为左右排版、双图对比或拆页。
- 每页左上角页眉位置保持一致；标题、副标题、横线和内容区不得拥挤。
- 手动换行和自动换行都必须保护英文完整单词；不要按字符数硬切中英文混排文本，必要时禁用 PowerPoint 的 Latin mid-word line break。
- 中英文混排正文还必须避免行首孤立标点；换行检查不仅看英文 token，也要看每行开头是否出现顿号、逗号、句号、分号、冒号等标点。
- 正文句子不应过早手动换行；在不越界、不拆词的前提下，每行应尽量使用所属文本框的可用宽度。如果一行只写少量字就换行，应合并换行、放大字号或重排文本框。
- 公式多时必须拆页；每页最多 4 个公式，每个公式有科学简要解释。
- 多个重要图片不得硬塞一页；如果第二张图会变成缩略图，必须增加“补充图表/结果证据”页面。
- 页面不得出现内部证据 ID、本地路径、JSON 文件名、prompt/AI 生成说明或工具痕迹；只保留正式文献引用。
- 所有展示公式必须是标准 LaTeX 渲染结果；损失函数名称、优化器名称等若不是公式，应写成自然语言描述，不要伪装成 `FunctionName(...)` 公式。

## 6. 页面序列规划

（使用本 skill "Slide 结构定义" 章节中的推荐结构，
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

严格按顺序执行以下命令，审计失败不得导出：

```bash
python PPT生成skill/skills/ppt-master/scripts/layout_quality_audit.py <project_path> -s output --strict
python PPT生成skill/skills/ppt-master/scripts/total_md_split.py --project <project_path>
python PPT生成skill/skills/ppt-master/scripts/finalize_svg.py --project <project_path>
python PPT生成skill/skills/ppt-master/scripts/layout_quality_audit.py <project_path> -s final --strict
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
   - 证据映射仅用于 `_workflow` 内部追踪，不得写入公开 `ppt_brief.md`、页面脚注、SVG 文本或 PPT 可见内容。
4. 生成 `ppt_brief.md`。
5. 初始化 ppt-master 项目（`project_manager.py init`）。
6. 复制实验图表到项目 `images/` 目录。
7. 生成 `design_spec.md`（使用本 skill 中的模板骨架）。
8. 按 slide 结构定义逐页生成 SVG 文件。
9. 执行审计与后处理流程（layout_quality_audit output → total_md_split → finalize_svg → layout_quality_audit final → svg_to_pptx）。
10. 将最终 PPTX 复制到 `PPT/实验N/` 目录；只保留最终交付 PPT，删除旧版、中间版、细节修正版等多余 PPTX。
11. 验证最终 PPTX 为有效 zip 包、核心 XML 可解析、slide count 与页脚总数一致；若 PowerPoint 打开会提示修复，不得交付。
12. 用 PowerPoint 导出所有页面 PNG，运行文字边界检查，并人工查看封面、公式页、图表页、讨论页、总结页和感谢页。文字框边界检查应达到 `ISSUES=0`。
13. 检查 PPTX XML 中可编辑文本：凡包含 `[A-Za-z]` 的可见文本 run，`latin` 字体必须为 `Times New Roman`，中文 `eastAsia` 字体必须仍为宋体/雅黑等原定中文字体。
14. 检查所有可见可编辑文本是否存在英文 token 被换行拆开；不得出现 `Transforme/r`、`Embeddin/g`、`check/point`、`simple-exa/mples` 这类跨行断词。
15. 检查每个正文行的行首；不得出现以 `，`、`。`、`；`、`：`、`、`、`,`、`.` 等标点开头的孤立标点行。
16. 检查底部是否存在无文字、无信息价值的残余说明框；若存在必须删除。
17. 检查正文换行密度；不得出现明显“几个字就换行”且右侧仍有大量空余的正文排版。
18. 检查所有图表页的真实图片来源和渲染结果；网络结构、流程图、训练曲线、混淆矩阵、样例预测等必须显示真实实验图，不能显示装饰叶片、空白图或错误图片。
17. 将 `pptx_path`、`ppt_brief.md`、关键 SVG 页面和导出命令写回 `_workflow`。

---

## 状态追踪交接

PPT 完成后，使用 `experiment-state-tracker` 更新：

- `workflow_state.yaml` 中的 `ppt` 和 `phase8_ppt`：
  ```yaml
  phase8_ppt:
    status: completed
    updated_at: YYYY-MM-DD
    outputs:
      brief_path: code/workN code/_workflow/ppt_brief.md
      project_path: PPT生成skill/projects/<name>/
      pptx_path: PPT/实验N/实验N PPT.pptx
      slide_count: quality_adaptive
  ppt:
    brief_path: code/workN code/_workflow/ppt_brief.md
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

注意：`workflow_state.yaml` 中可以保留 `evidence` 字段用于内部追踪，但这些字段不得出现在最终 PPT 或任何面向听众的页面文案中。

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
- 在 PPT 可见内容中暴露内部证据 ID、本地路径、JSON 文件名、prompt、AI/工具生成说明或调试痕迹。
