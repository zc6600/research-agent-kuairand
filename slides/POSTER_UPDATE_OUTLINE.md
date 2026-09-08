# 海报更新大纲 / Luna 执行交接

日期：2026-09-08。当前阶段仅制定大纲，未修改海报。

## 1. 内容基准与输出方向

- 以当前本地最新版主线 PPT 为准：`slides.md`、`scripts/prepare-main-deck.mjs` 及其引用组件。主线为 8 页 + 2 页附录；不能只读取 Markdown 而漏掉 Evaluation 卡片内页和 Problem 翻面内容。
- 推荐沿用已有 A0 竖版 Voyage 海报的象牙白、深蓝、赭石与航海插画，更新叙事和信息结构。执行基底默认 `posters/html/voyage/poster.html` 与 `poster.css`；这是版式建议，并非用户已指定的版本。
- 创建 `posters/html/main-deck-update/` 独立版本，保留现有海报供对照。正文英文；说明文档可中文。
- 核心叙事：研究为什么难以持续 → 系统怎样持续研究 → 五条证据 → 如何开始。
- 让读者能在海报上直接看到图、数字和恢复案例。所有核心内容静态展开，无悬停、翻面、滚动和链接替代正文。

## 2. 版面与内容大纲

### A. 页首：项目与主张（约 12% 高度）

**SciOdyssey**

副标题：**A research layer over your agent harness.**

主张：**Our agent can carry a research task to completion.**

机制摘要：**Preserve the research world. Reset the researcher.**

用小字限定实验证据：KuaiRand-Pure · fixed evaluator · public validation。插画作为识别元素，避免挤压证据区。

### B. 左栏上部：Problem → Design

标题：**What sustained research needs**

从 PPT P2–P3 提炼三个压力：预设工作流遇到未知问题、单条推理轨迹形成惯性且需要科学有效性审查、分支搜索重复读取上下文。

以四个短标签连接系统设计：**Adaptive tools / Fresh reasoning / Audited evidence / Reusable context**。不展开三张翻面卡全部细节；8× read/edit 与 4.5× 投影测算不作为主海报数字，避免分散资源账本的口径。

### C. 左栏主体：System

标题：**One persistent world. Fresh scientific judgment.**

主图：Environment → Research World → Fresh Scientist → META → 回写 Research World。

- Environment：任务、数据与评估器、baseline、预算与权限。
- Research World：证据与实验账本、可修正的研究摘要与先验、保留的实现 State。
- Scientist：假设、代码、实验、解释、报告；拥有科学判断。
- META：审查 claim ↔ evidence、限定结论、维护记忆与 State；决定哪些内容持续存在。
- 在 World → Scientist 之间标明 context reset；下方一条 Harness + runtime 承载工具、隔离、日志、产物与执行。
- 并行搜索只保留小支线：isolated branches → review → explicit adoption，避免与串行主循环争夺面积。

### D. 右栏主体：Evaluation（主要阅读区）

五个静态证据模块按最新版 PPT 顺序排布，标题与证据在同一模块内。不用扇形重叠卡片。

**01 · The model got better.**

- 一组紧凑对照柱/表：官方 FM Primary **0.6016000** → SciOdyssey **0.6059363**，绝对提升 **+0.0043363**。
- GAUC **0.6728421**；nDCG@5 **0.5390304**。
- 最终实现：46 leak-free categorical fields · 8-seed FM · NumPy / CPU。
- 分数集中在该证据图内，不再增加独立的大数字栏。

**02 · The search kept going.**

- 四轮横向轨迹：valid baseline → representation expansion → variance reduction → strongest retained recipe。
- 各轮保留分数：0.6016310 → 0.6040901 → 0.6044289 → 0.6059363。
- 标注 **4 cycles / 13 named experiments / 7 Full evaluations**。
- 若使用七点图，数据直接取 `EvaluationTrajectory.vue`；曲线表示保留的 Full 验证前沿，不把所有实验画成连续改善。

**03 · Our agent is robust.**

- 三步恢复图：`numpy.float32` serialization failure → Scientist repairs writer and reruns → evidence retained and reviewed。
- 短说明：训练和评估已完成，失败发生在证据写入；打印测量结果仍存在，修复后重新运行并保存证据。
- 必须准确区分：Scientist 修代码，META 审查与管理持久化；不能写成 META 亲自修复代码。该事件中无人手动选择修复或编辑代码。

**04 · Our agent beat Codex on this task.**

- 推荐简明双值对照：direct Codex Goal **0.6044533**，SciOdyssey **0.6059363**，差值 **+0.0014830**。
- Codex 保留 **provisional** 标签；限定为该任务上的记录结果，不能暗示跨任务优势、同预算因果结论或统计显著性。
- 旧海报和现有嵌入散点图仍写 ≈0.6046；原始 `direct-codex-goal-baseline.md` 给出 0.6044532703，应按此更新数值和图形坐标。
- 默认不搬旧的多条件 token 散点图，减少与第 05 模块重复。如要保留，先逐点核对运行身份、token 范围与 score 的对应关系。

**05 · We are not tokenmaxxing**

- 项目投入：**~US$10 subscription-equivalent usage**，一周的 GPT Plus + Gemini Pro 使用折算，**1 × MacBook M2**。
- 独立标注 retained-run telemetry：**48.240M total tokens（含 cache-read） / 4.020M non-cache input + output / 0 GPU-hours**。
- ~US$10 是项目级折算估计；不是按 API 标价计算的实付费用，也不是 48.240M tokens 的结算价格。两个统计范围分别说明。

### E. 底部通栏：Experience

标题：**Start your journey.**

副标题：**Autonomous by default. Supervisable by design.**

输入：`task.md` = what to solve；`PERSONAL.md` = how to work。

流程：**Define → step → run → parallel → inspect**；旁边放一个精简 Coding agent 输入框：

> Use the research-agent skill. Follow task.md and PERSONAL.md. Let me review the results and evidence.

将 P5 动画转为静态流程，不搬字幕、时间轴或 Dashboard 底部已删除的 RETAINED STATE / PRIMARY 分数栏。

### F. 收尾与页脚

- 一条主要观察：**Diversity is a prior.** 多种 Scientist 可拓宽先验，现有实验未隔离证明其增益。
- P8 工程实践最多缩成两句小字：每个 agent 独立 branch；通过 GitHub 留下可审查的后续任务。明确为 proposed practice；空间不足优先删这一项。
- 一句边界：当前证据来自单个任务的 public validation；META、State 和 reset 的独立效应尚未隔离。
- 团队、仓库地址与二维码。二维码作为获取代码的入口，核心证据仍完整呈现在海报中。

## 3. 空间与取舍

建议：页首 12%，双栏正文 68%，Experience 14%，收尾/页脚 6%；正文左栏约 44%、右栏约 56%。比例可随实际排版调整。

正文删减优先级：装饰 → 工程实践细节 → harness 品牌列表 → 多条件对照散点图。保留主循环、五条证据与开始入口。不要通过不断缩小字号填满内容。

旧海报的独立 Motivation 并入 System；Recovery 从 Insights 移到第三证据模块；旧多条件散点图收敛为该任务 Codex 对照；新增明确资源投入模块；Experience 改为 Start your journey。

## 4. Luna 执行步骤与来源

1. 开始时重新读取本地最新文件与 git status，当前 PPT 存在用户持续修改，不能用旧 PDF 或远端覆盖本地源文件。
2. 基于 Voyage 新建独立版本，先组织英文正文与静态图，再适配 CSS。用户若另指定海报基底，则保留此内容结构迁移过去。
3. 数据来源：`components/EvaluationClaimCards.vue`、`EvaluationCardBody.vue`、`EvaluationTrajectory.vue`；系统来源：`slides.md` P4、`composables/insightSynthesis.ts`；体验来源：`ExperienceJourney.vue`。
4. 原始证据：`../competition_archive/kuairand-pure/reports/direct-codex-goal-baseline.md`（特别是 provisional 审计说明）、`../docs/FINAL_REPORT.md` §4.2、提交目录的 cycle-1 报告与验证记录。~US$10 依 PPT 标记估计，不能自行改为精确实付金额。
5. 输出可编辑 HTML/CSS、A0 PDF、预览 PNG 与简短 README；参考旧 Voyage 的 export.mjs。实施时使用适用的 PDF/浏览器检查技能。
6. 验收：五条证据均直接可见；图形坐标和数值一致；无重叠、裁切或隐藏内容；PDF 字体与图表清晰；保留 provisional、public validation、资源统计范围；不混入其他 PPT 改动。

交接指令：请按本文件实施海报新版本；先检查当前源文件更新，再落地排版、导出和视觉检查。本轮已完成大纲，尚未开始海报实现。
