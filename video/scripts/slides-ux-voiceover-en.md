# SciOdyssey · English AI voice-over

这份英文稿对应当前 Slidev User Experience 动画，时长 **2:07.2**。按短句分别生成，自动插入静音，使每句落在对应画面。语气自然、克制，保持 Keynote 的留白。

## Narration

### 00:00.8–00:08.5

SciOdyssey. A research layer over your agent harness. Your tools. One persistent research world.

### 00:09.4–00:12.2

Start with your research question.

### 00:13.7–00:19.8

Define the objective and how success will be measured.

### 00:20.7–00:27.8

Then set your working preferences: the environment, experiment budget, and boundaries.

### 00:29.2–00:32.2

One step. Then, review.

### 00:33.3–00:43.7

Run one research cycle with step. The Scientist investigates. Evidence is recorded. And control returns to you.

### 00:45.0–00:48.0

Or, let it run.

### 00:49.1–01:01.5

Set a cycle budget. A fresh Scientist continues the work each round, while the project carries the task, memory, and evidence forward.

### 01:02.8–01:05.6

Now, explore wider.

### 01:06.9–01:13.2

Use parallel to explore different directions in independent worktrees.

### 01:14.0–01:21.3

A Reviewer compares the evidence. Choosing a branch to adopt remains an explicit decision.

### 01:22.6–01:25.5

See what stays.

### 01:26.7–01:31.0

Open the dashboard to inspect the retained result.

### 01:31.7–01:41.0

See the score, the implementation state, and the evidence behind it. Then decide what comes next.

### 01:42.4–01:45.4

Already in your workflow.

### 01:46.5–01:49.8

Use the research-agent skill.

### 01:50.1–01:54.0

Explore in parallel. Let me review what to keep.

### 01:54.5–01:59.2

Research workflow, connected. Task, memory, and evidence stay with the project.

### 02:00.3–02:06.0

SciOdyssey. Let research run. Start your journey.

## 生成 AI 配音

已提供脚本 `generate-slides-voiceover.mjs`，正文与时间轴源文件为 `slides-ux-voiceover-en.json`。默认使用 OpenAI 的 `gpt-4o-mini-tts` 和 `marin` 声音，可通过环境变量 `TTS_VOICE` 更换声音。参数已通过 [OpenAI 官方语音文档](https://developers.openai.com/api/docs/guides/text-to-speech) 核对。

需要 Node.js 20+、FFmpeg、ffprobe 和有语音 API 使用权限的 OpenAI API key。当前环境已找到 FFmpeg，但没有 `OPENAI_API_KEY`，所以尚未生成真实配音。

在仓库根目录执行（zsh，密钥输入不会回显）：

```zsh
read -rs 'OPENAI_API_KEY?OpenAI API key: '
export OPENAI_API_KEY
node video/scripts/generate-slides-voiceover.mjs
unset OPENAI_API_KEY
```

运行会调用付费语音 API。每次使用新的输出目录，不覆盖已有录音。脚本逐句生成 WAV，检查长度，最后合成为 **127.2 秒**的 `voiceover.wav`。它也会保留所有分句 WAV 和实际长度报告。超时的句子不会被裁断或强制加速：保留音频并报告问题，不输出不完整的合成轨。缩短相应英文句子后再生成，或在剪辑软件里手动调整。

只检查稿件和时间轴，不调用 API：

```sh
node video/scripts/generate-slides-voiceover.mjs --dry-run
```

## 给视频加上声音

1. 录制 [当前 UX 页面](http://localhost:3030/5)：开始录屏后点击 Replay，完整播放，保持标签页在前台。剪掉 Replay 之前的准备画面，让动画零点对应视频零点。
2. 把视频和生成的 `voiceover.wav` 导入你使用的剪辑软件，旁白放在 **00:00**。声音文件已包含开头及各句之间的留白，不要再去掉静音。
3. 核对每个目的标题与语音入点。若录屏掉帧造成时间变长，使用保留的分句 WAV 按实际切点微调。尤其试听 SciOdyssey 的发音、skill 指令和结尾。
4. 导出 MP4；如加字幕，手动校对产品名和命令。对外展示时注明 “AI-generated voice-over”。

当前页面是 Vue 动画，旧的 `npm run render:keynote` 只会导出原来的 72 秒版本，不能用它作为本稿的底片。脚本不修改页面，也不录屏；语音生成完成后仍需实际试听与音画检查。
