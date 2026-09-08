# Research Agent · Slidev

SciOdyssey 全英文技术演示（含英文讲者备注）：9 页主线 + 3 页附录，白底、彩色重点，16:9。内容以仓库 README、技术报告及架构文档为依据，讲者备注保留来源及证据口径。

## 叙事顺序

| 部分 | 页码 | 核心内容 |
| --- | --- | --- |
| 封面 | 1 | 项目与叙事路线 |
| Problem | 2–3 | 研究任务与长期自主研究的障碍 |
| System | 4 | Insight 汇聚成架构 |
| Experience | 5 | 输入任务与研究工作流 |
| Evaluation | 6 | 结果、轨迹、恢复与审计证据卡片 |
| Insights | 7–9 | 经验、工程实践、收束 |
| 附录 | 10–12 | 开放能力、团队与补充能力对比 |

## 本地演示

需要 Node.js 22.12 或更高版本。在本目录运行：

```bash
npm ci
npm run dev
```

打开 http://localhost:3030 。方向键切页，`P` 打开讲者模式，`O` 打开总览。

第三页翻开并收起卡片时，对应 insight 会在底部点亮。点击 `Build the system` 或按右方向键进入第四页，会播放约四秒的 insight 汇聚与架构展开动画。点击动画区域可直接完成，第四页右上角 `Replay` 可重播。减少动态效果模式和 PDF 导出直接展示完整架构。

第五页 UX 动画默认按英文讲稿时间轴显示底部字幕；静态模式和 PDF 导出会隐藏字幕。

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

## PPT 演示版本

- `slides.md`：原版主线演示 PPT（现代简洁科技风），配套 `SciOdyssey-main.pdf`。
- `slides-voyage.md`：**新版本 Voyage 航海典藏风格 PPT**，继承海报 `05-voyage` 的象牙质感纸张底纹（Ivory Paper）、复古衬线大标题（Times New Roman）、海洋深蓝与赤陶赭石撞色（Blue & Rust）、以及手绘风主视觉封面。
  - 本地预览：`npm run voyage:dev`（访问 http://localhost:3032 ）
  - 导出 PDF：`npm run voyage:export`（生成 `SciOdyssey-voyage.pdf`）
- `slides-3d.md`：**新版本 3D 空间交互风格 PPT（Spatial 3D Edition）**，在深空暗色科技底色上，全方位引入交互式 WebGL/Three.js 3D 场景与 CSS 3D 景深架构，配套 `SciOdyssey-3d.pdf`。
  - 核心 3D 视觉元素：
    - `<SpatialGlobe3D />`：3D 全息研究世界粒子天球与多层轨道环
    - `<Landscape3D />`：3D 动态假说地势曲面，直观展示局部陷阱与自主多盆地跃迁轨迹
    - `<ArchitectureStack3D />`：3D 爆炸式立体分层架构（科学家机群 / 纯证据边界 / 持久世界）
    - `<HypothesisGraph3D />`：3D 假说星系空间分支网络，动态修剪失败假说与强化优胜轨迹
    - `<PrismChart3D />`：3D 发光立体棱镜对比柱状图（KuaiRand AUC / GAUC / 冷启动）
    - `<Card3D />`：支持鼠标悬停 3D 倾斜、景深视差（Parallax）与动态光斑的科技卡片
  - 本地预览：`npm run 3d:dev`（访问 http://localhost:3033 ）
  - 导出 PDF：`npm run 3d:export`（生成 `SciOdyssey-3d.pdf`）

## Poster 版本

- `poster.md`：原版，保留不变。
- `poster-editorial.md`：方法结构优先，强化研究世界、角色和交接关系。
- `poster-evidence.md`：证据优先，强化验证图表、分数表和实验记录。
- `poster-type.md`：字体实验版，标题使用本地衬线字体，标签与命令使用本地等宽字体。

导出 3 个新版本：

```bash
npm run poster:variants
```

输出分别为 `SciOdyssey-poster-editorial.pdf`、`SciOdyssey-poster-evidence.pdf` 和 `SciOdyssey-poster-type.pdf`。

框架用法参考 [Slidev 官方文档](https://sli.dev/guide/)；构建和导出参数参考 [CLI 文档](https://sli.dev/builtin/cli)。

## Evaluation 卡片试版

`npm run dev` 的第 6 页为 Evaluation 卡片页。点击卡片后，图表、数据和正文直接呈现在展开的卡片内，长内容在卡片内部滚动。五张卡片依次承载模型结果、持续搜索、失败恢复、Codex 对照，以及 P10 的自主性与资源账本。`BACK TO HAND` 或 Esc 返回卡片组。

原来的结果、轨迹和审计顺序页面已从主线移除。卡片内容在 `components/EvaluationCardBody.vue`，卡片交互在 `components/EvaluationClaimCards.vue`；修改数据时需与 `slides.md` 保持一致。
