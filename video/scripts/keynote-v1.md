# SciOdyssey — Your research. Your rhythm.

独立对比版：`SciOdysseyKeynoteFilm`。72 秒，1920×1080，30fps。
基于已有 UX 的产品内容、浅色科学视觉与流动轨迹；原有 compositions 和成片保留。

## 导演判断

现有 workflow 版本反复使用「标题 + 说明 + 多个 UI 卡片」，每个段落重新搭建一个版面，观众需要重新阅读。新版本把操作放大成画面主角：同一个工作窗口承接命令、研究轨迹、证据和下一次选择。镜头的远近由任务决定：输入时靠近命令，运行时后退看进展，并行时拉开看分支，检查时推进证据。

发布会感来自清晰的揭示、动作后的停顿、产品的分量感和连续的空间关系。白色舞台、Avenir Next、原 slides 的蓝色作为主要强调色；保留真实 Dashboard 自身配色。每次只让一个动作成为注意力中心。没有章节页码、固定角标或功能列表。

## 时间轴 / 先定脚本，再实现

| 时间 | 英文旁白草稿 | 镜头、画面与动作 | 承接关系 |
|---|---|---|---|
| 00–05 | Your research. Your rhythm. | 大字出现，蓝色短线像输入光标一样停顿。一个终端从字下方显现，镜头靠近。 | 蓝线成为贯穿研究过程的进度线。 |
| 05–15 | Start with one step. A fresh scientist explores. The evidence stays. The next move is yours. | 特写输入 `step`，按下回车后退到完整工作窗口。一个光点依次经过 META、Scientist、Evidence，最终停在 Your turn。 | 命令仍留在原位，观众看见一次运行结束后的控制权。 |
| 15–25 | Or give it room to run. Set a cycle budget, and let the research continue. | 同一行的 `step` 替换成 `run`，下方补入 `--max-cycles 4`。一条轨迹分成四段，连续点亮，镜头慢慢后退。 | 已积累的轨迹不清空；从串行进展展开到并行空间。 |
| 25–35 | Explore several directions at once. Independent worktrees. A reviewer compares the evidence. | `parallel` 命令，画面拉宽。一条线分成三条，三位 Scientist 在不同轨道推进，然后交给 Reviewer。 | 分支共同抵达证据边界，窗口继续扩展为 Dashboard。 |
| 35–46 | And see what the work actually produced. The state. The result. The evidence behind it. | 完整真实 Dashboard 截图建立产品可信度。随后在窗口内向下移动至真实 retained validation 区域，停留于 S004 与 Primary。 | 保留窗口边框与位置；从观察证据转向明确的人工决定。 |
| 46–55 | When you want to choose, take the lead. Inspect the review. Explicitly adopt a branch. | Dashboard 退到背景；终端浮到前景，输入完整 `parallel-promote` 示例命令。回车只在停顿之后发生。 | 同一条研究轨迹继续，控制权被交回用户。 |
| 55–64 | Or bring the research skill into your coding agent. The same world, in your own workflow. | `SKILL.md` 文件标记沿蓝线进入通用 coding-agent 界面。自然语言请求变为使用 research-agent skill 的操作意图，外部 world 文件仍在下方。 | 不假设任何特定 coding agent 的 slash-command API。 |
| 64–72 | Let it run. Make it yours. SciOdyssey. | 窗口退场，留下轨迹。三条线重新收束为一条下划线，结尾主张与品牌出现并留白停顿。 | 收束开头的 rhythm 主题。 |

## 内容真实性

- `step` 是最多一次 Scientist 的 META session；`run` 是最多给定 cycle budget，可提前收敛；轨迹节点表示 cycle/evidence，不能暗示每次必有新 checkpoint。
- `parallel` 使用独立 worktrees；Reviewer 是事后评审。示例分支 `r1b1/r1b2/r1b3` 不附虚构成绩。
- Dashboard 使用 `public/assets/dashboard-overview.png` 与 `dashboard-validation.png`。这是现有 KuaiRand 案例，不能把真实 retained score 暗示成影片中示意 parallel run 的结果；画面注明 recorded example。
- 证据特写先展示真实截图，再把截图中 Primary 的显示值 `0.605936` 原样重排为矢量文字，保证放大后清晰；不做增长计数或改变精度的动画。
- Dashboard 是只读观察界面。人工采用分支通过 CLI 表现，不制造 Dashboard 中不存在的 promote 按钮。
- `parallel-promote` 展示 `--target`、`--parallel-dir`、`--branch`、`--allow-edits`。示例路径说明为 demo，不能当成项目真实运行路径。
- 根目录 `SKILL.md` 是外部 coding-agent 文档；runtime agents 使用 launcher 注入的角色材料。影片中的 coding-agent UI 是概念演示，不声称这是特定厂商的实际界面。
- 来源：`SKILL.md`、`src/research_agent/cli.py`、`src/research_agent/parallel.py`、`slides/slides.md`、`docs/dashboard/1.png`、`docs/dashboard/2.png`。

## 声音与交付

此版为 code-first Remotion animatic：先验镜头、节奏与操作叙事。英文旁白稿已写好，尚未录制。提供可关闭的轻量原创合成节奏底与输入/完成提示音，单独保存音轨，后续可替换正式音乐、旁白与音效。

声音节拍：5s 输入靠近；10.5s 一次确认；16s 连续执行起拍；25.5s 空间展开；35s 收束；46s 留出人工决策停顿；53s 确认；55s 文件进入 Agent；65s 最终落点。字幕可通过 props 开启用于检查旁白对时。

交付：独立脚本、keynote 源码目录、Studio composition、MP4、关键帧。检查命令可读性、转场前后物体连续、截图资源、边界帧、音轨、旧版文件完整性。最后由用户并排比较旧 workflow 与新版的镜头和节奏，决定后续正式配音与细修方向。
