# Research Agent · Slidev

11 页全英文技术演示（含英文讲者备注）。黑底、荧光绿、终端字体，16:9。内容以仓库 README、技术报告及架构文档为依据，每页讲者备注附来源和必要的口径说明。

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

静态站点生成在 `dist/`；PDF 输出为 `research-agent.pdf`。首次导出若缺少 Chromium，运行 `npx playwright install chromium`。

## 编辑

- `slides.md`：内容、顺序与讲者备注。
- `styles/theme.css`：颜色、字体与版式。
- `slide-top.vue`：统一页脚和页码。

使用本地系统字体，不依赖在线字体服务。尊重系统减少动态效果设置。

框架用法参考 [Slidev 官方文档](https://sli.dev/guide/)；构建和导出参数参考 [CLI 文档](https://sli.dev/builtin/cli)。
