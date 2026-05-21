# CLAUDE.md

国科大深度学习课程实验自动化 agent 的项目总控文件。
8 阶段流水线、13 个 skill、`_workflow/` 状态追踪系统。
核心原则：**正确性 > 可复现 > 证据链可追溯 > 形式美观**。
完整实验交付必须包含代码、实验报告和 PPT；PPT 是最后阶段的必做任务，不需要用户额外明确要求。
数据集准备必须先于正式训练完成；训练命令不得把下载动作隐藏在首次数据加载中。

## 意图路由

当用户请求涉及完成、开始、继续某个深度学习实验时，**必须**立即启动 workflow.md 的 8 阶段流水线，从 Phase 1 开始。不得跳过阶段、不得直接写代码或报告。

触发模式（不限于此）：
- "完成实验N"、"做实验N"、"帮我做实验N"、"实验N的作业"
- "开始实验N"、"继续实验N"、"完成第N个实验"
- 任何包含"实验"和一个编号或名称、且语义为"执行该实验"的请求

路由动作：立即加载 `skills/experiment-router/SKILL.md` → 执行 Phase 1 路由 → 按 workflow.md 依次推进 → 每阶段只加载该阶段指定的 skill。

非实验执行请求（如"解释 ViT 原理"、"帮我看看这段代码"）不触发流水线，正常回答。

## 目录结构

```
work/
├── skills/                        # 各阶段 skill（按需加载，不预加载）
├── code/                          # 所有实验代码工作区的父目录
│   └── workN code/                # 实验 N 专属工作区（名称含空格 + " code" 后缀）
│       └── _workflow/             # 状态三件套：workflow_state.yaml, artifacts_manifest.yaml, execution_log.md
├── 实验要求（来自国科大在线）/       # 每个实验的 PDF 与可选伴随数据资产
│   └── 实验N要求/                   # 实验 N 的 PDF、压缩包、npz、csv 等本地资产
├── 实验报告模板_latex/              # main.tex + UCASReport.sty
├── PPT生成skill/                   # ppt-master 流程入口
└── workflow.md                     # 唯一 canonical 阶段导航（8 阶段、skill 加载、切换条件）
```

## 运行环境

- Conda 环境：`python_cuda`，Python 3.12.12，PyTorch 2.9.0+cu128，CUDA 12.8
- Python 完整路径：`D:\anaconda\anaconda_envs\envs\python_cuda\python.exe`
- 命令前缀：`& 'D:\anaconda\anaconda_envs\envs\python_cuda\python.exe' -s -X utf8`
  - `-s`：防止 AppData user-site 覆盖 Conda 包路径
  - `-X utf8`：确保 Windows 下中文 stdout 正常输出
  - **不可省略这两个标志**
- LaTeX 编译：`xelatex` + ctexart 文档类（用于中文报告）

## 工作流

@workflow.md

按 workflow.md 定义的 8 个阶段推进。每阶段按文档指定加载对应 skill，不预加载全部 skill。
执行实验流水线时必须推进到 Phase 8 PPT 生成与复核后才算可交给用户审核；`项目提交/` 只在用户审核确认后同步最终版。

## 权威源优先级

多源冲突时按此顺序裁决：

1. 实验要求 PDF 及同目录伴随数据资产（`实验要求（来自国科大在线）/实验N要求/`）
2. 已验证的代码和测试结果
3. README 等说明文件

## 工作区隔离

- 实验 N 对应 `code/workN code/`，一个实验一个工作区，绝不共享
- 工作区名称格式：`workN code/`（注意空格 + "code" 后缀，不是 `workN/`）
- 若目录不存在，在 Phase 4 之前创建
- 状态三件套维护在 `code/workN code/_workflow/` 下

## 验证方法

各阶段确认工作正确的手段：

- 环境检查：`& 'D:\anaconda\anaconda_envs\envs\python_cuda\python.exe' -s -X utf8 -c "import torch; print(torch.cuda.is_available())"`
- 数据检查：正式训练前必须确认数据来源、数据目录和数据校验记录；本地伴随数据优先于外部下载
- 代码检查：在工作区内运行单元测试或 smoke test
- 训练检查：`_workflow/` 中指标文件存在，准确率达到 PDF 目标
- 报告检查：`xelatex` 编译无错误，PDF 文件存在且可打开
- 状态检查：`workflow_state.yaml` 的 `status` 字段与实际阶段一致

## 常见陷阱

- **工作区名称含空格**：是 `work1 code/` 而非 `work1/`，路径中必须带空格和 "code"
- **PDF 文件名使用混合中文标点**：如 `实验1+...` 用 `+`，`实验2：...` 用全角 `：`，不要自行构造文件名
- **实验要求目录可能含数据资产**：必须先枚举 `实验N要求/` 同目录文件；已有数据集优先使用，不要绕过本地资产去网上下载
- **不要盲目信任 PDF 中的示例代码**：可能含有意或无意的错误，必须验证
- **Conda 环境不是系统默认 Python**：必须使用完整路径，不能用 `python` 直接调用
- **`-s` 标志不可省略**：省略会导致 AppData 下的包覆盖 Conda 环境，引发 import 错误

## 不可违反的规则

1. 报告中的每一项声明必须可追溯到 `_workflow/` 中的证据文件
2. 未实际运行代码不得声明"已完成"或指标已达标
3. GPU 训练前必须先验证环境（Phase 3）
4. 正式训练前必须完成数据来源判定和数据就绪检查；若需外部开源数据，必须记录官方/学术来源、许可或使用说明
5. 报告撰写前必须通过 Phase 6 验证（`verification.status == passed`）
6. 未达 PDF 定义的目标指标不得假装成功，继续迭代或如实记录阻塞
7. 不隐藏未解决的阻塞项，必须明确记录到 `execution_log.md`
8. Phase 7 报告通过后必须进入 Phase 8 生成并复核 PPT；不得在 PPT 完成前声明完整交付
9. Phase 6/7/8 必须加载 `skills/experiment-deliverable-standards/SKILL.md`，并按其中的报告、流程图、PPT、草稿工作区标准做核验；只有用户审核确认后才按提交目录和 zip 标准做最终核验
