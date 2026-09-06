# Research Agent · Slidev

SciOdyssey 全英文技术演示（含英文讲者备注）：22 页主线 + 2 页附录，白底、彩色重点，16:9。内容以仓库 README、技术报告及架构文档为依据，讲者备注保留来源及证据口径。

## 叙事顺序

| 部分 | 页码 | 核心内容 |
| --- | --- | --- |
| 封面 | 1 | 项目与叙事路线 |
| Problem | 2–3 | 研究任务与长期自主研究的障碍 |
| Motivation | 4–5 | 开放能力与研究世界 / 研究者的不同生命周期 |
| System | 6–10 | 角色、架构、交接、记忆、并行探索 |
| Experience | 11–14 | 输入任务、实验轨迹、故障恢复、查看留存结果 |
| Evaluation | 15–18 | 验证分数、自主性、资源、直接 agent 对照 |
| Insights | 19–22 | 经验、局限、工程实践、收束 |
| 附录 | 23–24 | 团队与补充能力对比 |

## 本地演示

需要 Node.js 22.12 或更高版本。在本目录运行：

```bash
npm ci
npm run dev
```

打开 http://localhost:3030 。方向键切页，`P` 打开讲者模式，`O` 打开总览。

## 构建与导出

```bash
npm run build
npm run export
```

静态站点生成在 `dist/`；主稿 PDF 输出为 `SciOdyssey-main.pdf`。首次导出若缺少 Chromium，运行 `npx playwright install chromium`。

## 编辑

- `slides.md`：内容、顺序与讲者备注。
- `styles/theme.css`：颜色、字体与版式。
- `slide-top.vue`：统一页脚和页码。

使用本地系统字体，不依赖在线字体服务。尊重系统减少动态效果设置。

框架用法参考 [Slidev 官方文档](https://sli.dev/guide/)；构建和导出参数参考 [CLI 文档](https://sli.dev/builtin/cli)。
