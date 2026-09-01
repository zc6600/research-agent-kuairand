# Engineering

只记录可复用的工程事实与工作流：入口、命令、成本量级、诊断方法。
一次性的执行细节写进对应实验的 events，不要在这里堆积。
无法帮助未来实验设计的记录，就不要写。

## How does the current system run?

当前系统从数据到训练到 evaluation 的实际运行方式是什么？
最重要的入口、命令和依赖是什么？

## How can I run a medium-fidelity hypothesis gate?

如果只是想验证一个机制假设，应该如何运行一个 medium 规模、低成本
但仍然有区分力的 gate？固定使用一个低成本的数据范围、预注册的 control、
固定 seed 和有限 epoch；说明需要改什么参数或脚本，以及大概多久。这个
gate 只能决定是否值得做 full 实验，不能被当作最终 benchmark 结果。
开始 gate 前，说明为什么该 Medium 足以支持当前假设，并记录代表性校准
依据和升级到 Full 的条件。

代表性校准是判断 Medium 是否保留当前决策所需的数据结构和信号。根据任务
说明校准依据、采用的检查及升级到 Full 的条件，实际方法和结果写入项目记录。

## How can I diagnose and compare bottlenecks?

在形成正式 bottleneck 之前，应该如何记录可复用的诊断入口、原理分析、
竞争解释和消融结果？优先保留能区分多个机制的 medium 规模诊断，包括
learning/time curve、error/distribution slice、component ablation 或
counterfactual control；避免把无边界的调参 sweep 写成 bottleneck 证据。
如果 medium 无法保留关键结构或统计功效不足，bottleneck discovery 可以
直接使用完整训练集和 public validation；hidden test 仍然不可使用。

## How can I run a large / full experiment?

接近正式结果的实验应该怎么运行？
需要什么资源？
大概多久？

## What does an experiment cost?

目前已经测量过哪些运行时间？
哪些只是估计？
不同 fidelity 的大致成本是多少？

## What hardware and resources are available?

当前 CPU / GPU / memory / disk / accelerator 情况是什么？
有哪些已知限制？

## Where should I modify the system?

如果要修改：
- model
- feature
- loss / training
- evaluation-related research code
- experiment fidelity

分别应该从哪里开始看？

## What must remain stable?

哪些东西是 benchmark / evaluation contract 的一部分，
不应该为了涨分而修改？

## What engineering facts have changed?

最近的 research 是否发现了会影响后续实验设计的工程事实？
