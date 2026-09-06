# SciOdyssey · 终端版演示

这是 `slides/slides.md` 主线 deck 的终端原生版本：24 页叙事保留，视觉改成 ANSI 颜色、Unicode 线条、终端流程图、表格和指标条。实现不依赖第三方 npm 包，适合 SSH、纯 ANSI 终端和没有图形协议的环境。

## 运行

在仓库根目录执行：

```bash
node terminal/present.mjs
```

也可以使用目录内的 npm script：

```bash
npm --prefix terminal start
```

常用命令：

```bash
node terminal/present.mjs --slide 15   # 从第 15 页开始
node terminal/present.mjs --print 15   # 输出第 15 页并退出，适合录屏/管道
node terminal/present.mjs --list       # 打印目录
node terminal/present.mjs --check      # 检查 80×24 和 120×36 终端布局
node terminal/present.mjs --auto 8     # 每 8 秒自动翻页
node terminal/present.mjs --no-color   # 关闭 ANSI 颜色
```

交互时支持方向键、`h/j/k/l`、空格翻页；`n` 看讲者备注，`o` 看目录，数字键跳页，`?` 看帮助，`q` 退出。

## 技术栈判断

| 方案 | 核心技术 | 适合场景 | 取舍 |
| --- | --- | --- | --- |
| 当前仓库 Slidev | Markdown + Vue 3 + Vite + Playwright | 浏览器演示、PDF、PPTX/PNG 导出 | 画面自由度高，但依赖浏览器渲染 |
| `presenterm` | Rust + Markdown + ANSI TUI | 终端原生演示、代码、图片、备注、主题 | 功能最完整，需要安装二进制 |
| `patat` | Haskell + Pandoc + ANSI | Markdown、讲者备注、代码片段、自动播放 | 生态成熟，但需要 Pandoc/Haskell 运行环境 |
| `tpp` | Ruby + ncurses | 传统纯文本终端 | 兼容面广，但项目和语法较老 |
| `chafa` + 图形协议 | C + ANSI/Unicode/Sixel/Kitty/iTerm2 | 把 PNG 等图像尽量贴近原画面地放进终端 | 需要图像转换工具，终端兼容性取决于协议 |
| 本目录实现 | Node.js ESM + ANSI escape + Unicode | 当前项目零安装依赖的终端版 | 采用终端原生重排，不复刻浏览器像素级布局 |

### 为什么本版本选 Node + ANSI

`presenterm` 是更适合长期维护的通用终端演示引擎；本项目这次先采用内置 Node 运行器，是因为仓库已经使用 Node/Slidev，且不新增 Rust、Haskell、ncurses 或图像转换依赖。终端版把重点放在可读性和可验证的证据数字上，并提供窄终端降级。

如果后续需要像素级显示现有 PNG/PDF，可在 `presenterm` 或 `chafa` 上增加图像后端：Kitty、iTerm2、WezTerm、Ghostty、foot 等终端支持的图形协议不同，SSH/tmux 还需要额外配置。当前版本故意不把这类环境差异放进默认启动路径。

## 内容来源

- [主线 Slidev 源文件](../slides/slides.md)
- [最终技术报告](../docs/FINAL_REPORT.md)
- [项目 README](../README.md)
- [终端版内容与渲染器](deck.mjs) / [present.mjs](present.mjs)

外部技术资料：

- [`presenterm` 官方文档](https://mfontanini.github.io/presenterm/)
- [`presenterm` GitHub](https://github.com/mfontanini/presenterm)
- [`patat` GitHub](https://github.com/jaspervdj/patat)
- [`tpp` GitHub](https://github.com/cbbrowne/tpp)
- [`chafa` GitHub](https://github.com/hpjansson/chafa)
- [Kitty graphics protocol](https://github.com/kovidgoyal/kitty/blob/master/docs/graphics-protocol.rst)
- [iTerm2 inline images protocol](https://iterm2.com/documentation-images.html)
- [Slidev 官方文档](https://sli.dev/guide/)
