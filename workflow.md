# workflow.md

本文件是 `work` 项目的轻量工作流索引。
它只定义阶段顺序、阶段输入输出和应加载的 skill，不承载硬性约束、命令细节和写作细则。
所有阶段性细节应写入 `skills/` 中，由执行时按需加载。

## 1. 工作流定位

- `CLAUDE.md`：项目总控入口
- `workflow.md`：唯一 canonical 阶段导航与任务编排
- `skills/`：各阶段的详细执行规则

## 2. 核心输入与目标位置

- `实验要求（来自国科大在线）/`：每个实验的要求子目录，包含实验 PDF 和可选伴随数据资产
- `code/`：所有实验代码工作区的统一父目录
- `code/work* code/`：实验代码工作区目录命名模式
- `code/workN code/_workflow/`：该实验的跨阶段状态、产物清单和执行日志目录
- `实验报告模板_latex/`：实验报告模板
- `skills/`：项目技能目录
- `PPT生成skill/`：ppt-master 流程入口

说明：

- `N` 必须严格对应用户真实需求中的实验编号。
- 一个实验必须且只能对应 `code/` 下一个独立的 `workN code/` 子目录。
- 不允许多个实验共用同一个代码工作区。
- 报告和 PPT 只能引用 `_workflow` 中已有证据支撑的要求、指标、命令结果和产物。
- PPT 是完整实验任务的必交付物，始终作为最后阶段执行，不以用户是否额外明确要求为触发条件。
- 数据资产优先级：实验要求子目录中的本地数据文件 > PDF 指定的官方/标准数据集 > 经验证的外部开源数据源。正式训练前必须完成数据就绪检查。

## 3. 跨阶段状态文件

每个实验必须维护：

- `code/workN code/_workflow/workflow_state.yaml`
- `code/workN code/_workflow/artifacts_manifest.yaml`
- `code/workN code/_workflow/execution_log.md`

这些文件由 `skills/experiment-state-tracker/SKILL.md` 负责维护。

## 4. 标准阶段

### Phase 1：实验定位

- Goal：把用户请求映射到唯一实验、唯一要求子目录、唯一 PDF、伴随数据资产和该实验专属代码工作区
- Inputs：用户请求、实验 PDF 目录、`code/` 下现有 `work* code/` 目录
- Load：
  - `skills/experiment-router/SKILL.md`
  - `skills/experiment-state-tracker/SKILL.md`
- Outputs：`experiment_id`、`experiment_name`、`requirement_dir`、`pdf_path`、`companion_files`、`code_dir`、`code_dir_state`

### Phase 2：实验要求解析

- Goal：从 PDF 和同目录数据资产中提取可执行要求、指标、提交物、数据来源和证据来源
- Inputs：`pdf_path`、`requirement_dir`、`companion_files`
- Load：
  - `skills/experiment-requirement-reader/SKILL.md`
  - `skills/experiment-state-tracker/SKILL.md`
- Outputs：`requirement_summary`、`target_metrics`、`deliverables`、`dataset_requirements`、`provided_assets`、`requirement_evidence`

### Phase 3：环境核验

- Goal：确认本地 Conda/Python/PyTorch/CUDA 和关键依赖可用
- Inputs：`code_dir`、`code_dir_state`、`requirement_summary`
- Load：
  - `skills/experiment-environment-checker/SKILL.md`
  - `skills/experiment-state-tracker/SKILL.md`
- Outputs：`runtime_profile`、`recommended_command_prefix`、`environment_status`

### Phase 4：代码基线检查

- Goal：识别目标代码工作区现状、缺口、已有产物和实现起点
- Inputs：`code_dir`、`code_dir_state`、`requirement_summary`
- Load：
  - `skills/experiment-code-baseline/SKILL.md`
  - `skills/experiment-state-tracker/SKILL.md`
- Outputs：`baseline_summary`、`implementation_plan`

### Phase 5：算法实现、数据准备入口与资产准备

- Goal：在该实验专属工作区完成实现、数据准备/检查入口、测试入口、训练评估入口和基础可视化资产接口
- Inputs：`code_dir`、`requirement_summary`、`runtime_profile`、`baseline_summary`、`implementation_plan`
- Load：
  - `skills/experiment-code-implementer/SKILL.md`
  - `skills/experiment-state-tracker/SKILL.md`
- Outputs：`implementation_result`、`data_preparation_plan`、`verifier_handoff`

### Phase 6：严格测试、训练、评估与图表资产

- Goal：先完成数据就绪检查，再运行正式测试、训练和评估，判断指标是否达标，并形成报告/PPT 可复用的指标与图表资产
- Inputs：`code_dir`、`target_metrics`、`verifier_handoff`
- Load：
  - `skills/experiment-verifier/SKILL.md`
  - `skills/experiment-diagram-maker/SKILL.md`
  - `skills/experiment-state-tracker/SKILL.md`
- Outputs：`data_readiness`、`verification_result`、`metrics_summary`、`report_assets`

### Phase 7：实验报告生成与复核

- Goal：基于真实结果生成 LaTeX 报告，并在交付前复核证据链和编译结果
- Inputs：`workflow_state.yaml`、`artifacts_manifest.yaml`、`execution_log.md`、报告模板、验证产物、图表资产
- Load：
  - `skills/experiment-report-writer/SKILL.md`
  - `skills/experiment-report-reviewer/SKILL.md`
  - `skills/experiment-state-tracker/SKILL.md`
- Outputs：`report_tex`、`report_pdf`、`report_review`

### Phase 8：PPT 生成与复核

- Goal：基于已完成报告和证据链生成、导出并复核可编辑 PPT，作为完整实验交付的最后阶段
- Inputs：`workflow_state.yaml`、`artifacts_manifest.yaml`、`execution_log.md`、`report_pdf`、`report_assets`
- Load：
  - `skills/experiment-ppt-writer/SKILL.md`
  - `PPT生成skill/CLAUDE.md`
  - `PPT生成skill/skills/ppt-master/SKILL.md`
  - `skills/experiment-state-tracker/SKILL.md`
- Outputs：`ppt_brief`、`ppt_file`

## 5. 阶段切换条件

- Phase 1 完成后，才能进入 Phase 2。
- Phase 2 完成后，才能进入 Phase 3 和 Phase 4。
- Phase 3 与 Phase 4 完成后，才能进入 Phase 5。
- Phase 5 完成后，才能进入 Phase 6。
- Phase 6 通过或阻塞项被如实记录后，才能进入 Phase 7。
- Phase 7 报告复核通过后，必须进入 Phase 8。
- Phase 8 完成并登记 PPT 产物后，才可最终交付完整实验任务。

## 6. Skill 设计要求

- 一个 skill 只负责一个明确阶段或子阶段。
- 硬性约束、检查项、命令细节、异常处理应写入对应 skill。
- `workflow.md` 不复制 skill 内容，只负责引用与编排。
- 若某阶段 skill 尚未存在，应优先补全 skill，而不是继续扩写本文件。
