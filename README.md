# DL Experiment Automation Skills

基于 Claude Code 的深度学习课程实验自动化流水线。包含 8 阶段 workflow、11 个 skill，可自动完成从实验定位到代码实现、训练评估、报告撰写、PPT 生成的全流程。

> **适用范围说明**
>
> 本项目最初是为**中国科学院大学（UCAS）深度学习课程**的实验作业设计的，因此部分 skill 中包含与该校课程相关的硬编码配置（如特定的目录命名、LaTeX 模板命令、Conda 环境名等）。
>
> 如果你不是国科大学生，**本项目的核心流水线架构和方法论仍然完全可用**——只需根据下方 [复用改造指南](#复用改造指南) 修改对应的 skill 文件即可适配你自己的学校和课程。
>
> 简而言之：**框架和思路是通用的，涉及具体学校/课程的配置是可替换的。**

## 功能概览

| 阶段 | Skill | 说明 |
|------|-------|------|
| Phase 1 | experiment-router | 实验定位：将用户请求映射到具体实验 |
| Phase 2 | experiment-requirement-reader | 要求解析：从 PDF 提取可执行要求与指标 |
| Phase 3 | experiment-environment-checker | 环境核验：检查 Conda/Python/PyTorch/CUDA |
| Phase 4 | experiment-code-baseline | 代码基线：识别工作区现状与缺口 |
| Phase 5 | experiment-code-implementer | 算法实现：完成代码编写与数据准备 |
| Phase 6 | experiment-verifier + experiment-diagram-maker | 测试训练：运行训练、评估指标、生成图表 |
| Phase 7 | experiment-report-writer + experiment-report-reviewer | 报告生成：LaTeX 报告撰写与复核 |
| Phase 8 | experiment-ppt-writer | PPT 生成：基于报告生成可编辑 PPT |

贯穿全程：`experiment-state-tracker` 维护跨阶段状态文件。

## 目录结构

```
your-project/
├── CLAUDE.md                  # 项目总控配置（需修改为你自己的环境）
├── workflow.md                # 8 阶段工作流定义
├── skills/                    # 各阶段 skill
├── tools/                     # 工具脚本
│   └── workflow_consistency_check.py
├── code/                      # 实验代码工作区（运行时生成）
│   └── workN code/            # 每个实验独立的工作区
├── 实验要求/                   # 放置你的实验 PDF 和数据资产
├── 实验报告模板_latex/          # 放置 LaTeX 报告模板
└── PPT生成skill/               # 放置 PPT 生成工具
```

## 前置要求

### 1. Claude Code

本项目基于 [Claude Code](https://docs.anthropic.com/en/docs/claude-code)（Anthropic 官方 CLI agent）运行。请先安装并配置 Claude Code。

### 2. Python 环境

- Python 3.10+
- PyTorch（建议 CUDA 版本）
- Conda 或其他虚拟环境管理器

### 3. LaTeX 环境（报告生成必需）

PPT 和报告的生成依赖 LaTeX 环境。下面是详细的配置指南。

#### Windows 用户

**方案 A：安装 TeX Live（推荐）**

1. 访问 [TeX Live 官网](https://tug.org/texlive/)，下载安装程序（约 4-5 GB 完整安装，或选择最小安装后按需添加包）
2. 运行 `install-tl-windows.exe`
3. 安装完成后，确认 `xelatex` 可用：
   ```bash
   xelatex --version
   ```

**方案 B：安装 MiKTeX**

1. 访问 [MiKTeX 官网](https://miktex.org/download)，下载 Windows 安装包
2. 安装时选择"自动安装缺失的包"
3. 安装完成后，确认 `xelatex` 可用

**必需的 LaTeX 包：**

无论选择哪种发行版，确保以下包已安装：

| 包名 | 用途 | 安装方式（TeX Live） |
|------|------|---------------------|
| `xecjk` | 中文排版核心 | `tlmgr install xecjk` |
| `ctex` | 中文文档类 | `tlmgr install ctex` |
| `fontspec` | 字体选择 | `tlmgr install fontspec` |
| `geometry` | 页面布局 | `tlmgr install geometry` |
| `graphicx` | 图片插入 | `tlmgr install graphicx` |
| `booktabs` | 专业表格 | `tlmgr install booktabs` |
| `amsmath` | 数学公式 | `tlmgr install amsmath` |
| `hyperref` | 超链接 | `tlmgr install hyperref` |
| `biblatex` | 参考文献管理 | `tlmgr install biblatex` |

**必需的系统字体：**

- **宋体（SimSun）**：Windows 自带，中文字体默认选择
- **Times New Roman**：Windows 自带，英文字体默认选择
- 如果使用其他操作系统，可能需要手动安装这些字体或修改模板中的字体配置

**编译命令：**

```bash
# 标准编译流程（含参考文献）
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex

# 简单编译（无参考文献）
xelatex main.tex
```

#### Linux 用户

```bash
# Ubuntu/Debian
sudo apt install texlive-full texlive-lang-chinese texlive-xetex

# Arch Linux
sudo pacman -S texlive-basic texlive-lang-chinese texlive-xetex
```

#### macOS 用户

```bash
brew install --cask mactex
# 或最小安装
brew install --cask basictex
sudo tlmgr install xecjk ctex fontspec
```

### 4. 配置实验报告模板

你需要将自己的实验报告 LaTeX 模板放置在 `实验报告模板_latex/` 目录下。

**推荐的报告模板来源：**

- **[UCAS-templates](https://github.com/Chengyue-Lu/UCAS-templates)**：适用于中国科学院大学学生的各类 LaTeX 模板，包含报告撰写、课程论文、Beamer 演示、课堂笔记、课后作业等。其中 `For 报告撰写` 目录下的 `UCASReport.sty` 和 `main.tex` 可直接使用。

**模板目录结构示例：**

```
实验报告模板_latex/
├── main.tex          # 报告主文件
├── UCASReport.sty    # 报告样式文件
└── figures/          # 图片资源目录
    └── logo.pdf      # 校徽等图片
```

**使用方法：**

1. 从 [UCAS-templates](https://github.com/Chengyue-Lu/UCAS-templates) 下载或 clone
2. 将 `For 报告撰写/` 目录下的文件复制到 `实验报告模板_latex/`
3. 根据需要修改 `main.tex` 中的课程名称、学生信息等

如果你使用其他学校的模板，只需确保模板支持 `xelatex` 编译和中文显示（ctex 或 xecjk），然后放入该目录即可。

### 5. 配置 PPT 生成工具

PPT 生成（Phase 8）需要一个 PPT 生成工具。你需要将其放置在 `PPT生成skill/` 目录下。

**推荐的 PPT 生成工具：**

| 项目 | 地址 | 说明 |
|------|------|------|
| **ppt-master** | [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | AI 生成原生可编辑 PPTX，支持模板复制、动画、TTS 旁白。基于 SVG 生成真正的 PowerPoint 形状，而非图片。MIT 协议。 |

**ppt-master 安装步骤：**

```bash
# 克隆到 PPT生成skill/ 目录
git clone https://github.com/hugohe3/ppt-master.git PPT生成skill

# 安装 Python 依赖
pip install -r PPT生成skill/requirements.txt
```

**ppt-master 主要特性：**

- 真正的 PowerPoint 输出：所有元素可直接在 PowerPoint 中点击编辑
- 模板复制：可将任何 `.pptx` 文件转为可复用模板
- 动画支持：页面过渡动画和逐元素入场动画
- 多模型支持：Claude、GPT、Gemini 等
- 跨平台：Windows、macOS、Linux

**其他可选的 PPT 相关工具：**

- [python-pptx](https://github.com/scanny/python-pptx)：Python 原生 PPTX 生成库，适合自定义脚本
- [Marp](https://github.com/marp-team/marp)：Markdown 转 PPT/HTML/PDF

## 快速开始

### 1. 获取本项目

```bash
git clone https://github.com/let778750-cpu/-PPT-.git
cd -PPT-
```

### 2. 配置环境

编辑 `CLAUDE.md` 中的 **运行环境** 部分，将 Python 路径、Conda 环境名等替换为你自己的配置：

```markdown
## 运行环境

- Conda 环境：`your_env_name`，Python 3.12，PyTorch 2.x+cu12x
- Python 完整路径：`/path/to/your/python`
- 命令前缀：`/path/to/your/python -s -X utf8`
```

### 3. 配置目录

按上面的指南完成：
- 安装 LaTeX 环境并放入报告模板到 `实验报告模板_latex/`
- 安装 ppt-master 到 `PPT生成skill/`
- 将你的实验 PDF 要求文件放入 `实验要求/实验N要求/`

### 4. 使用

在 Claude Code 中，直接告诉它你要完成某个实验：

```
请帮我完成实验1
```

Claude Code 会自动按 8 阶段流水线推进：定位实验 → 解析要求 → 环境核验 → 代码基线 → 实现 → 训练验证 → 报告 → PPT。

## 工作原理

本项目的核心是 `workflow.md` 定义的 8 阶段流水线，每个阶段由对应的 `skills/` 下的 skill 文件驱动：

1. **实验定位**：解析用户请求，找到对应的实验 PDF 和工作区
2. **要求解析**：从 PDF 提取可执行指标、数据集需求
3. **环境核验**：验证 Python/CUDA/依赖是否就绪
4. **代码基线**：检查工作区现有状态，制定实现计划
5. **算法实现**：编写代码、准备数据、设置训练脚本
6. **训练验证**：运行训练、评估指标、生成图表资产
7. **报告生成**：基于真实结果撰写 LaTeX 报告
8. **PPT 生成**：基于报告和图表生成可编辑 PPT

每个实验维护 `_workflow/` 状态目录（`workflow_state.yaml`, `artifacts_manifest.yaml`, `execution_log.md`），确保全程可追溯。

## 复用改造指南

本项目 11 个 skill 按与国科大课程的耦合程度分为三档。下表列出了每个 skill 的耦合等级、包含的学校特定内容，以及你改造时需要做什么。

### 耦合程度总览

| 耦合等级 | Skill | 学校特定内容 | 改造工作量 |
|----------|-------|-------------|-----------|
| **高** | experiment-report-writer | `UCASReport.sty` 模板、`\setUCAS*` 封面命令、ctexart 字体配置 | 需替换整个 LaTeX 模板层 |
| **中** | experiment-router | 目录名 `实验要求（来自国科大在线）/`、中文标点文件名规则 | 替换目录名和文件名匹配逻辑 |
| **中** | experiment-code-implementer | 数据资产路径 `实验要求（来自国科大在线）/实验N要求/`、`work1 code` 参考实现 | 替换路径引用 |
| **低** | experiment-state-tracker | `code/workN code/` 路径模式、`实验报告/实验N/` 输出路径 | 替换路径常量 |
| **低** | experiment-environment-checker | Conda 环境名 `python_cuda`、Python 版本 | 改为你自己的环境名 |
| **低** | experiment-diagram-maker | 图表输出路径 `实验报告/实验N/figures/` | 替换输出路径 |
| **低** | experiment-report-reviewer | `\experimentsectionpage` 命令检查 | 适配你的 LaTeX 模板命令 |
| **低** | experiment-ppt-writer | 课程名"深度学习"、受众"课程教师、助教" | 替换课程名和目标受众 |
| **极低** | experiment-requirement-reader | 描述文字中提到"国科大" | 仅改描述文字即可 |
| **极低** | experiment-code-baseline | 一处 `work1 code` 作为布局示例 | 仅改示例路径即可 |
| **极低** | experiment-verifier | `code/workN code/` 路径模式 | 仅改路径即可 |

### 逐 Skill 改造要点

#### experiment-report-writer（改造量最大）

这是与国科大耦合最深的 skill。它直接调用了 `UCASReport.sty` 提供的封面命令：

```
\setUCASCoverTitle{...}
\setUCASReportTitle{...}
\setUCASCourseName{...}
\setUCASAuthorName{...}
\setUCASStudentID{...}
\setUCASCollege{...}
\setUCASAdminClass{...}
\setUCASTrainingUnit{...}
```

**改造方式：**
1. 将 `实验报告模板_latex/` 替换为你学校的 LaTeX 报告模板
2. 打开 `skills/experiment-report-writer/SKILL.md`，找到"封面命令"相关的章节
3. 将上述 `\setUCAS*` 命令替换为你模板中对应的封面/元信息命令
4. 如果你的模板使用不同的文档类（如 `article` 而非 `ctexart`），还需调整字体配置和编译命令
5. 报告的四段式结构（实验内容 → 理论基础 → 算法设计 → 实验总结）是通用的学术报告结构，通常可以直接保留

#### experiment-router（中等改造量）

此 skill 硬编码了国科大在线平台的目录结构：

```
实验要求（来自国科大在线）/     ← 实验要求根目录
└── 实验N要求/                   ← 具体实验的要求子目录
```

**改造方式：**
1. 在 SKILL.md 中搜索 `实验要求（来自国科大在线）`，替换为你自己的实验要求目录名（如 `assignments/` 或 `实验要求/`）
2. 如果你的文件命名不含中文全角符号，删除关于 `+`、`：` 等中文标点的匹配规则
3. 工作区命名格式 `code/workN code/`（含空格和"code"后缀）如果你觉得不习惯，可统一改为 `code/expN/` 等格式——但需要同步修改所有其他 skill 中的路径引用和 `CLAUDE.md`

#### experiment-code-implementer（中等改造量）

引用了国科大特定的数据资产路径和参考实现：

```
实验要求（来自国科大在线）/实验N要求/    ← 伴随数据资产路径
work1 code                               ← 被当作标准布局参考
```

**改造方式：**
1. 替换数据资产路径为你的实验要求目录
2. 如果你有自己的"标准实现"作为参考，修改对应引用；如果没有，删除该参考即可
3. 代码布局规范（README、train/evaluate 脚本、package 目录、tests/、outputs/、figures/、data/）是通用的工程实践，建议保留

#### experiment-environment-checker（低改造量）

在"核验建议"章节中写死了 Conda 环境名：

```
优先检查 Conda 环境 `python_cuda` 与 Python `3.12.12`
```

**改造方式：** 改为你自己的环境名和 Python 版本，或者改为"从 `CLAUDE.md` 的运行环境部分读取"（当前版本已做此处理）。

#### experiment-ppt-writer（低改造量）

在内容模板中包含课程特定信息：

```
课程名称（如'深度学习'）
目标受众：课程教师、助教
```

**改造方式：** 替换为你自己的课程名和目标受众。

#### 其余 skill（极低改造量）

以下 skill 只在描述文字或示例路径中提到国科大相关内容，改动极小：

- **experiment-requirement-reader**：仅描述中提到"国科大"，核心逻辑（PDF 解析、结构化提取）完全通用
- **experiment-code-baseline**：仅一处用 `work1 code` 作布局示例
- **experiment-state-tracker**：路径模式 `code/workN code/` 是目录约定而非学校绑定，改路径即可
- **experiment-diagram-maker**：输出路径 `实验报告/实验N/figures/` 可按需替换
- **experiment-report-reviewer**：检查 `\experimentsectionpage` 命令是否正确——如果你换了模板，改为检查你模板中的对应命令
- **experiment-verifier**：核心验证逻辑（数据就绪检查、训练执行、指标比对）完全通用

### 最小改造清单

如果你只想快速跑起来，最少需要改动以下内容：

1. **`CLAUDE.md`**：替换"运行环境"部分的 Python 路径、Conda 环境名
2. **`experiment-router/SKILL.md`**：替换 `实验要求（来自国科大在线）/` 为你的实验要求目录名
3. **`experiment-report-writer/SKILL.md`**：替换 `\setUCAS*` 封面命令为你模板的对应命令
4. **`实验报告模板_latex/`**：放入你学校的 LaTeX 报告模板
5. **`PPT生成skill/`**：放入 ppt-master 或其他 PPT 生成工具

完成以上 5 处修改后，整个流水线即可用于你自己的课程实验。

### 目录路径统一替换

如果你想把所有中文目录名改为英文（或你习惯的命名），需要在以下文件中同步替换：

| 原路径 | 涉及文件 |
|--------|---------|
| `实验要求（来自国科大在线）/` | `CLAUDE.md`, `experiment-router/SKILL.md`, `experiment-code-implementer/SKILL.md` |
| `实验报告模板_latex/` | `CLAUDE.md`, `experiment-diagram-maker/SKILL.md`, `experiment-report-writer/SKILL.md` |
| `实验报告/实验N/` | `experiment-state-tracker/SKILL.md`, `experiment-diagram-maker/SKILL.md` |
| `code/workN code/` | `CLAUDE.md`, `workflow.md`, 以及所有包含该路径的 skill |
| `PPT生成skill/` | `CLAUDE.md`, `workflow.md`, `experiment-ppt-writer/SKILL.md` |
| `PPT/实验N/` | `experiment-ppt-writer/SKILL.md` |

## 致谢

- [ppt-master](https://github.com/hugohe3/ppt-master) - AI 生成原生可编辑 PPTX
- [UCAS-templates](https://github.com/Chengyue-Lu/UCAS-templates) - 国科大 LaTeX 模板集合
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) - Anthropic 官方 CLI agent

## 许可证

MIT License
