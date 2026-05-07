---
name: experiment-report-writer
description: 基于已验证的实验代码、训练结果和 _workflow 证据链，使用 LaTeX 模板生成国科大深度学习实验报告。适用于代码已通过验证、训练已完成、workflow 状态已记录后，需要生成实验报告 .tex 和 .pdf 的场景。
---

# 实验报告撰写器

## 概述

在 Phase 7 使用这个 skill。
它负责把 `requirement_summary`、`metrics_summary`、`artifacts_manifest`、`workflow_state.yaml` 和 `execution_log.md` 中的真实证据写入 LaTeX 报告模板，并编译为 PDF。

这个 skill 不替代任何验证阶段；它只依据已验证的证据链撰写报告。没有证据的结论不得写入报告。

## 前置条件

进入报告阶段前，必须确认：

- `code/workN code/_workflow/workflow_state.yaml` 存在且实现与验证阶段已经完成
- `verification.overall_passed == true`，或未达标项已经在 `open_issues` 中如实记录且用户接受生成未达标报告
- `code/workN code/_workflow/artifacts_manifest.yaml` 存在且包含训练产物
- `code/workN code/_workflow/execution_log.md` 存在且包含训练和评估命令记录
- `data_readiness` 已记录数据来源、数据目录和训练前检查命令
- `verification.metrics` 中所有硬性指标已达标（或阻塞项已记录）
- 验证阶段的关键产出物文件实际存在
- 报告所需图表资产已经由 `experiment-diagram-maker` 生成或明确标记为缺失

如果任何前置条件未满足，返回上一阶段补齐证据，不要凭空撰写报告。

## 输入

- `requirement_summary`
- `metrics_summary`
- `artifacts_manifest`
- `code/workN code/_workflow/workflow_state.yaml`
- `code/workN code/_workflow/execution_log.md`
- `实验报告模板_latex/main.tex`
- `实验报告模板_latex/UCASReport.sty`
- 已登记的图表、流程图、指标 JSON、运行摘要

## 输出目录规则

报告模板目录只作为只读模板来源使用，不承载具体实验报告正文或编译产物。

每个实验的报告包必须生成到：

```text
实验报告/实验N/
  实验N报告.tex
  实验N报告.pdf
  UCASReport.sty
  figures/
  evidence/
```

规则：

- `N` 必须与真实实验编号一致。
- 不得覆盖或改写 `实验报告模板_latex/main.tex`。
- 需要编译报告时，将 `UCASReport.sty`、校徽和报告图表复制到 `实验报告/实验N/`。
- 所有新生成的报告 `.tex`、`.pdf`、编译日志、报告图表和报告证据副本都应放在 `实验报告/实验N/` 下。
- 模板目录中的 `main.tex` 只能保持模板骨架，不能写入某个实验的正文内容。

## 输出

返回结构化报告结果：

```yaml
report_result:
  status:
  report_tex_path:
  report_pdf_path:
  sections_completed: []
  evidence_coverage:
    all_claims_traced: true | false
    untraced_claims: []
  compilation:
    engine: xelatex
    success: true | false
    warnings: []
```

允许的 `status` 值：

- `completed`
- `partial`
- `blocked`
- `needs_clarification`

## 报告模板结构

模板文件 `实验报告模板_latex/main.tex` 定义了四个一级部分：

1. **一、实验内容** — 实验目标、输入、任务描述和验收要求；不得放置公式推导
2. **二、实验原理** — 与本实验相关的理论背景、算法原理、数学公式
3. **三、实验算法设计** — 算法设计思路、关键实现细节、代码说明
4. **四、实验总结** — 实验结果、指标分析、结论与改进方向

每个部分通过 `\experimentsectionpage{标题}` 开启新页。

封面信息通过以下命令设置：

```latex
\setUCASCoverTitle{实验报告}
\setUCASReportTitle{实验名称}
\setUCASCourseName{课程名称}
\setUCASAuthorName{姓名}
\setUCASStudentID{学号}
\setUCASCollege{学院}
\setUCASAdminClass{行政班级}
\setUCASTrainingUnit{培养单位}
```

## 写作风格规范

整体写作风格参考计算机学科顶会顶刊（如 NeurIPS、ICML、CVPR）的实验部分，但适配实验报告的特点：

- **精确用词**：技术术语准确，不使用模糊口语化表述。
- **定量优先**：能用数字说明的地方不用定性描述（如"准确率从 91.6% 提升到 99.3%"优于"准确率大幅提升"）。
- **逻辑清晰**：每段有明确论点，段落之间有逻辑衔接。
- **图文配合**：重要的结构、流程、结果必须有图或表支撑，不堆砌纯文字。
- **忠实覆盖**：实验报告不是论文，不追求 novelty，追求对实验要求的完整、准确覆盖。

注意区分：论文追求创新性，实验报告追求**对实验要求的忠实回应**。风格是手段，覆盖要求才是目的。

## 字体与排版

使用模板 `UCASReport.sty` 的默认设置，不额外修改字体配置：

- 正文：宋体 小四（12pt）— 由 `ctexart` 文档类的 12pt 选项和默认中文字体决定
- 章节标题：黑体 小三 — 由 `main.tex` 中 `\experimentsectionpage` 的 `\heiti\zihao{-3}` 决定
- 页眉：仿宋 — 由 `UCASReport.sty` 中 `\fangsong` 决定
- 页边距：上下左右各 2.5cm — 由 `UCASReport.sty` 中 `geometry` 宏包设定

不要在 `main.tex` 中额外添加字体覆盖命令。如果发现模板默认设置与实验要求不符，先确认后再修改。

## 数学公式规范

### 格式要求

- 行内公式使用 `$...$`，独立公式使用 `\begin{equation}...\end{equation}` 或 `\begin{align}...\end{aligned}`
- 独立公式必须有编号（使用 `equation` 或 `align` 环境），方便正文引用
- 公式中符号首次出现时必须定义含义
- 多行公式使用 `align` 或 `aligned` 环境，对齐符 `&` 放在等号处

### 字号

公式与正文保持相同字号（12pt），不额外放大。公式通过以下方式获得视觉突出：

- 独立成行居中显示
- 上下标和分数结构自带的视觉层次
- 编号和正文交叉引用

对于需要特别强调的关键公式，使用 `tcolorbox` 加框突出（模板已引入该宏包）：

```latex
\begin{tcolorbox}[colback=gray!5, colframe=black, title=核心公式]
\begin{equation}
  \mathcal{L}(\theta) = -\frac{1}{N}\sum_{i=1}^{N}\sum_{c=1}^{C} y_{i,c}\log(\hat{y}_{i,c})
\end{equation}
\end{tcolorbox}
```

### 符号一致性

同一篇报告中，同一物理量或数学概念必须使用统一符号：

- 实验原理中定义的符号，在算法设计和实验总结中必须保持一致
- 不允许前面用 $\theta$ 后面变成 $w$（除非有明确的符号映射说明）
- 建议在实验原理首次引入符号时给出定义表或逐一定义

## 图表规范

### 图片要求

- 格式优先级：PDF 矢量图 > SVG > PNG（位图不低于 300 DPI）。正式报告中优先引用 PDF 矢量图；同目录可保留 SVG 副本用于检查或复用。
- 使用 `\includegraphics` 插入，路径相对于 `.tex` 文件
- 不要在报告中硬编码绝对路径
- 图片文件应放置在 `实验报告/实验N/figures/` 子目录中

### 标题与编号

- 每张图必须有中文标题，最终 PDF 中应呈现为："图 X. 描述内容"
- 每个表必须有中文标题，最终 PDF 中应呈现为："表 X. 描述内容"
- 图表编号后使用英文句点 `.`，不得使用冒号 `：` 或 `:`
- 使用 `\caption{}` 设置标题，`\label{}` 设置交叉引用标签
- 引用时使用"如图 \ref{fig:xxx} 所示"或"见表 \ref{tab:xxx}"
- 在 LaTeX 中可使用 `caption` 宏包设置 `labelsep=period`

### 表格

- 使用标准 LaTeX 表格环境（`tabular`、`table`）
- 三线表优先，避免过度竖线分割
- 数据列右对齐，文本列左对齐
- 训练结果、对比实验等数据应使用表格呈现

## 流程图与示意图

### 位置要求

在"三、实验算法设计"中，必须在合适位置放置算法流程图，用于直观展示算法的整体流程或关键步骤。其他部分如需要说明网络结构、数据流向等，也应配图。

### 工具选择

按优先级选择：

1. **draw.io MCP 工具**（如已安装）：使用 draw.io 生成流程图，导出为 PDF 或 PNG（300 DPI+），通过 `\includegraphics` 插入报告
2. **LaTeX TikZ**（备选方案）：使用 `tikz` 宏包直接在 `.tex` 中绘制流程图，零外部依赖。适用于结构较简单的流程图

### 流程图规范

- 图中文字使用中文
- 节点形状区分语义：矩形=处理步骤，菱形=判断，圆角矩形=开始/结束
- 流程方向自上而下或自左而右，保持一致
- 箭头清晰，避免交叉
- 字体大小与正文协调，不小于五号（10.5pt）

## 代码展示规范

### 环境

模板 `UCASReport.sty` 已引入 `listings` 和 `pythonhighlight` 宏包。

优先使用 `pythonhighlight`（如果编译通过）：

```latex
\begin{python}
def forward(self, x):
    x = self.conv1(x)
    x = self.pool(x)
    return x
\end{python}
```

如果 `pythonhighlight` 包不可用（非标准 TeX Live 包），使用 `listings` 作为 fallback：

```latex
\lstset{
  language=Python,
  basicstyle=\small\ttfamily,
  keywordstyle=\color{blue},
  commentstyle=\color{gray},
  stringstyle=\color{red},
  numbers=left,
  numberstyle=\tiny\color{gray},
  frame=single,
  breaklines=true,
  showstringspaces=false
}

\begin{lstlisting}[caption={前向传播}, label={lst:forward}]
def forward(self, x):
    x = self.conv1(x)
    x = self.pool(x)
    return x
\end{lstlisting}
```

### 内容要求

- 只放关键核心代码片段，不放完整文件
- 每个代码片段应有简要说明，解释该片段的作用
- 代码中的注释应使用中文
- 代码片段应有标题和标签，方便引用

## 各部分撰写要求

### 一、实验内容（约 1-2 页）

从 PDF 要求和 `requirement_summary` 提取，需覆盖：

- 实验目标：本次实验要解决什么问题
- 数据或输入：使用了什么数据集、输入形式
- 数据来源：来自实验要求目录本地资产、标准公共数据集或已验证外部开源来源
- 任务定义：具体要完成什么任务
- 评价标准：用什么指标衡量效果
- 本节只做实验内容描述，不放置数学公式、形式化定义或损失函数推导；相关公式统一放到"二、实验原理"

页数是大致指引，不同实验可自然调整。

### 二、实验原理（约 2-4 页）

从 PDF 要求中识别本实验涉及的理论主题，围绕该主题展开原理阐述。具体理论范围由每个实验的 PDF 决定，不预设固定内容。

撰写原则：

- 理论内容必须服务于本实验，不堆砌无关背景
- 涉及的数学公式必须严格使用 LaTeX 数学环境（见"数学公式规范"）
- 符号首次出现时必须定义，且全文保持一致
- 如果实验涉及多个算法或技术的组合，应分别阐述各自原理后再说明组合方式

### 三、实验算法设计（约 3-5 页，核心章节）

从实际代码和实现中提取，需包含：

- 算法整体设计思路和架构
- 关键实现细节和核心逻辑
- 算法流程图（见"流程图与示意图"）
- 关键代码片段（见"代码展示规范"）
- 模型结构、数据处理、训练策略等设计选择及其理由

本部分是报告核心，必须有图（流程图、结构图）、有代码、有说明，三者配合。

### 四、实验总结（约 1-2 页）

从 `verification metrics` 和 `execution_log` 中提取，需包含：

- 实验结果：关键指标的定量报告
- 与目标对比：实际结果 vs PDF 要求，是否达标
- 结果分析：哪些设计选择有效，为什么
- 改进方向：如果重新做，可以尝试什么改进
- **全实验总结性收尾段**（必须）：在结果分析和改进方向之后，必须有一段总结性文字概括整个实验的全貌，需覆盖：实验目标回顾（做了什么、为什么做）、核心方法回顾（用了什么原理和算法设计）、关键结果回顾（取得了什么效果）、整体收获与意义（学到了什么、有何启示）。不能只停留在结果分析层面，要体现对整个实验全流程的回顾与升华。

所有指标数据必须来自 `_workflow` 中的真实记录。

### 参考文献格式规范

参考文献部分作为报告的最后一个一级部分，格式必须与其他一级标题保持一致。

#### 权威格式模板

所有参考文献条目的格式必须严格参照项目根目录下的 `references.bib` 模板文件。该文件定义了 12 种文献类型的标准格式，是引用格式的唯一权威来源。

**模板路径**：`references.bib`（项目根目录）

使用流程：
1. 确定文献类型（期刊、会议、书籍、学位论文、技术报告、预印本、在线资源、软件包、数据集、标准等）
2. 在 `references.bib` 中找到对应类型的条目示例
3. 参照该示例的字段结构和格式要求撰写 `\bibitem` 条目
4. 遵守文件附录中的 thebibliography 渲染格式规范

**格式总则**（与 `references.bib` 保持一致）：
- **作者数量**：≤ 3 位作者全部列出，最后一位前用 `and`；> 3 位作者列出前 3 位，后接 `, et al.`
- 作者名格式：使用全名（如 `Yann LeCun`，不是 `Y. LeCun`）
- 标题：sentence case（仅首单词首字母大写，专有名词除外）
- 期刊/会议名：使用 `\emph{}` 斜体
- 条目末尾以英文句点 `.` 结尾
- BibTeX key 命名：第一作者姓+年份+简短关键词

#### 页面与标题格式

- **另起一页**：参考文献必须从新页开始，与"一、实验内容"等标题行为一致
- **标题左对齐**：标题"参考文献"必须左对齐、黑体小三号，与其他一级标题格式完全一致
- **标题间距一致**：参考文献标题与下方文献条目之间的间距必须与前四个章节标题与正文之间的间距严格一致（均为 1em，由 `\experimentsectionpage` 宏控制）

#### LaTeX 实现方式

在 `.tex` 文件中，必须重定义 `thebibliography` 环境以移除其内置的 `\section*{\refname}` 调用（该调用会产生额外间距），然后插入：

```latex
\experimentsectionpage{参考文献}
\makeatletter
\renewenvironment{thebibliography}[1]%
  {\list{\@biblabel{\@arabic\c@enumiv}}%
       {\settowidth\labelwidth{\@biblabel{#1}}%
        \leftmargin\labelwidth
        \advance\leftmargin\labelsep
        \@openbib@code
        \usecounter{enumiv}%
        \let\p@enumiv\@empty
        \renewcommand\theenumiv{\@arabic\c@enumiv}}%
    \sloppy
    \clubpenalty4000
    \@clubpenalty\clubpenalty
    \widowpenalty4000%
    \sfcode`\.\@m}%
  {\def\@noitemerr
    {\@latex@warning{Empty `thebibliography' environment}}%
   \endlist}
\makeatother
\begin{thebibliography}{9}
```

该重定义保留了 `thebibliography` 的列表格式，但移除了内置的 `\section*{\refname}` 和 `\@mkboth`，使标题间距完全由 `\experimentsectionpage` 控制。

#### 文献质量与正文引用

- **文献质量**：引用文献必须为真实、权威、高质量且可在 Google Scholar 上检索到的学术文献；技术文档引用仅限框架官方文档
- **正文引用**：正文中通过 `\cite{key}` 引用参考文献，确保每个条目至少被引用一次
- **条目类型覆盖**：根据实际引用的文献类型，从 `references.bib` 中选择对应类型的格式模板，不得混用不同类型的字段

## 撰写流程

1. 读取 `_workflow/workflow_state.yaml`，确认实验编号、PDF 路径和当前状态。
2. 读取实验要求 PDF，提取理论范围和具体要求，确定"实验原理"需要覆盖的主题。
3. 读取 `_workflow/execution_log.md`，提取已执行的命令和关键输出。
4. 读取 `_workflow/artifacts_manifest.yaml`，确认训练产物和指标文件存在。
5. 读取 `dataset_requirements` 和 `data_readiness`，确认报告中的数据集描述、文件来源和预处理与真实数据准备记录一致。
6. 读取 `requirement_summary` 和 `metrics_summary`，明确报告需要覆盖的要求和指标。
7. 读取实际源码，确认算法描述与代码一致。
8. 读取或调用 `experiment-diagram-maker` 准备算法流程图、模型结构图和结果图。
9. 按四个部分撰写内容，遵循各部分的撰写要求和写作风格规范。
10. 确保报告中每个关键结论都能追溯到 `_workflow` 中的证据。
11. 使用 XeLaTeX 编译报告，处理编译错误直到成功。
12. 交给 `experiment-report-reviewer` 做 Phase 7 报告复核；复核通过后继续进入 Phase 8 PPT 生成。

## 证据追踪规则

报告中的每个关键声明必须满足：

- 指标值必须来自 `execution_log.md` 中记录的命令输出或 `artifacts_manifest.yaml` 中登记的文件
- 代码和算法描述必须与实际源码一致
- 实验配置必须与 execution_log 中记录的命令参数一致
- 数据集来源、样本规模和预处理必须与 `data_readiness`、数据准备日志或 manifest 中登记的文件一致
- 不允许引用未在 manifest 中登记的文件
- 不允许虚构未实际运行的实验结果

在撰写过程中，将每个报告声明对应的证据 ID 记录到 `workflow_state.yaml` 的 `report.claims` 中：

```yaml
report:
  claims:
    - id: claim-001
      text: "关键指标声明"
      evidence:
        - metric-001
        - artifact-013
      section: 四、实验总结
```

## LaTeX 编译

使用 XeLaTeX 引擎编译：

```bash
cd "实验报告/实验N"
xelatex "实验N报告.tex"
xelatex "实验N报告.tex"
```

编译两次以确保交叉引用和页码正确。

编译成功后：

- 将 `.tex` 和 `.pdf` 路径写入 `report_result`
- 将报告文件登记到 `artifacts_manifest.yaml`
- 更新 `workflow_state.yaml` 中 `phase7_report` 状态

编译失败时：

- 记录错误信息到 `report_result.compilation.warnings`
- 状态设为 `blocked`
- 如果是 `pythonhighlight` 包缺失，切换到 `listings` fallback 后重新编译
- 不要修改已有报告声称成功

## 状态追踪交接

报告完成后，使用 `skills/experiment-state-tracker/SKILL.md` 更新：

- `_workflow/workflow_state.yaml` 中的 `report` 和 `phase7_report`
- `_workflow/artifacts_manifest.yaml` 中新增的报告 `.tex`、`.pdf` 和图片文件
- `_workflow/execution_log.md` 中 LaTeX 编译命令记录
- `experiment-report-reviewer` 完成后写入报告复核结果

## 失败处理

- 如果前置条件未满足，返回 `blocked`，说明缺失的前置项。
- 如果证据链断裂（某个声明找不到支撑证据），停止撰写该部分并记录到 `untraced_claims`。
- 如果 LaTeX 编译失败，记录错误信息，状态设为 `blocked`，不要声称报告已生成。
- 如果 `pythonhighlight` 包不可用，切换到 `listings` fallback，不要卡在编译错误上。
- 如果实验指标未达标，如实报告实际指标和差距，不得虚构成达标。

## 边界

这个 skill 不得：

- 虚构实验结果、训练指标或未运行的命令
- 在代码未通过验证的情况下撰写报告
- 引用未在 `_workflow` 中登记的文件或结果
- 修改实验代码或其他实验的文件
- 跳过证据追踪直接输出报告内容
- 删除或覆盖历史执行日志和状态记录
- 为了通过编译而删除有意义的公式、图表或内容
