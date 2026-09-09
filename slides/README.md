# Research Agent · Slidev

SciOdyssey 全英文技术演示（含英文讲者备注）：12 页当前演示，白底、彩色重点，16:9。内容以仓库 README、技术报告及架构文档为依据，讲者备注保留来源及证据口径。

## 叙事顺序

| 部分 | 页码 | 核心内容 |
| --- | --- | --- |
| 封面 | 1 | 项目与叙事路线 |
| Talk order | 2 | 叙事路线 |
| Problem | 3–4 | 研究任务与长期自主研究的障碍 |
| System | 5 | Insight 汇聚成架构 |
| Experience | 6 | 输入任务与研究工作流 |
| Evaluation | 7 | 结果、轨迹、恢复与审计证据卡片 |
| Insights | 8–10 | 模型轮换、并行研究与工程实践 |
| 附录 | 11–12 | 开放能力与团队 |

## 本地演示

需要 Node.js 22.12 或更高版本。在本目录运行：

```bash
npm ci
npm run dev
```

打开 http://localhost:3030 。方向键切页，`P` 打开讲者模式，`O` 打开总览。

第四页翻开并收起卡片时，对应 insight 会在底部点亮。点击 `Build the system` 或按右方向键进入第五页，会播放约四秒的 insight 汇聚与架构展开动画。点击动画区域可直接完成，第五页右上角 `Replay` 可重播。减少动态效果模式和 PDF 导出直接展示完整架构。

第六页 UX 动画默认按英文讲稿时间轴显示底部字幕；静态模式和 PDF 导出会隐藏字幕。

## 构建与导出

```bash
npm run build
npm run export
```

静态站点生成在 `dist/`；主稿 PDF 输出为 `exports/current/SciOdyssey-main.pdf`。首次导出若缺少 Chromium，运行 `npx playwright install chromium`。

当前交付 PDF 统一放在 `exports/current/`；历史探索稿放在
`exports/archive/main-explorations/`。本地构建产物 `dist/`、`node_modules/` 和
`.generated-slides.md` 不纳入版本控制。

## 编辑

- `slides.md`：内容、顺序与讲者备注。
- `styles/index.css`：样式入口。
- `styles/foundation/`：设计 token、基础排版与少量通用工具类。
- `styles/theme.css`：历史主样式，下一阶段会逐步把页面专属段落迁入组件或 scene stylesheet。
- `slide-top.vue`：统一页脚和页码。

使用本地系统字体，不依赖在线字体服务。尊重系统减少动态效果设置。

## 主线 PPT

- `slides.md`：主线演示 PPT（现代简洁科技风），配套 `exports/current/SciOdyssey-main.pdf`。

## 历史版本

不再参与当前构建的 3D 和 Voyage slide deck 已归档，源文件与专属组件/样式位于：

- `archive/editions/3d/`：3D Spatial Edition；导出物位于 `exports/archive/editions/3d/`。
- `archive/editions/voyage/`：Voyage Editorial Edition；导出物位于 `exports/archive/editions/voyage/`。

它们不再出现在 `exports/current/`，也不再占用主线的 npm 命令和样式入口。`posters/html/voyage/` 是独立的 HTML 海报项目，仍与 slide deck 分开维护。

## Poster 版本

- `posters/slidev/poster.md`：原版，保留不变。
- `posters/slidev/poster-editorial.md`：方法结构优先，强化研究世界、角色和交接关系。
- `posters/slidev/poster-evidence.md`：证据优先，强化验证图表、分数表和实验记录。
- `posters/slidev/poster-type.md`：字体实验版，标题使用本地衬线字体，标签与命令使用本地等宽字体。

独立 HTML 海报项目位于 `posters/html/`：

- `posters/html/voyage/`：航海典藏风格海报。
- `posters/html/main-deck-update/`：主 deck 证据更新版海报。

可分别运行 `npm run poster:html:voyage` 和
`npm run poster:html:main-deck`；它们的 PDF 和本地 QA 产物保留在各自项目目录内。
完整的海报目录和命令说明见 [`posters/README.md`](posters/README.md)。

导出 3 个新版本：

```bash
npm run poster:variants
```

输出分别为 `exports/current/SciOdyssey-poster-editorial.pdf`、
`exports/current/SciOdyssey-poster-evidence.pdf` 和
`exports/current/SciOdyssey-poster-type.pdf`。

框架用法参考 [Slidev 官方文档](https://sli.dev/guide/)；构建和导出参数参考 [CLI 文档](https://sli.dev/builtin/cli)。

## Evaluation 卡片试版

`npm run dev` 的第 6 页为 Evaluation 卡片页。点击卡片后，图表、数据和正文直接呈现在展开的卡片内，长内容在卡片内部滚动。五张卡片依次承载模型结果、持续搜索、失败恢复、Codex 对照，以及 P10 的自主性与资源账本。`BACK TO HAND` 或 Esc 返回卡片组。

原来的结果、轨迹和审计顺序页面已从主线移除。卡片内容在 `components/EvaluationCardBody.vue`，卡片交互在 `components/EvaluationClaimCards.vue`；修改数据时需与 `slides.md` 保持一致。
