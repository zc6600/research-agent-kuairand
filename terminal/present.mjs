#!/usr/bin/env node

import process from "node:process";
import { slides } from "./deck.mjs";

const palette = {
  blue: [56, 189, 248],
  orange: [255, 135, 63],
  green: [62, 207, 142],
  purple: [166, 108, 255],
  rose: [255, 92, 120],
  white: [235, 241, 247],
  muted: [145, 160, 176],
  dim: [91, 106, 123],
  line: [54, 68, 84],
};

const argv = process.argv.slice(2);
const options = parseArgs(argv);
const useColor = !options.noColor && process.env.NO_COLOR === undefined;

if (options.help) {
  printHelp();
  process.exit(0);
}

if (options.list) {
  printOutline();
  process.exit(0);
}

if (options.check) {
  runLayoutCheck();
  process.exit(0);
}

let current = options.slide;
let mode = "slide";
let pendingJump = "";
let jumpTimer = null;
let autoTimer = null;

if (options.print || !process.stdin.isTTY || !process.stdout.isTTY) {
  process.stdout.write(renderFrame({ mode: "slide", index: current, clear: false }));
  process.exit(0);
}

startInteractive();

function parseArgs(args) {
  const parsed = {
    check: false,
    help: false,
    list: false,
    noColor: false,
    print: false,
    slide: 0,
    auto: 0,
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--help" || arg === "-h") {
      parsed.help = true;
    } else if (arg === "--list") {
      parsed.list = true;
    } else if (arg === "--check") {
      parsed.check = true;
    } else if (arg === "--print" || arg === "--once") {
      parsed.print = true;
    } else if (arg === "--no-color") {
      parsed.noColor = true;
    } else if (arg === "--slide" || arg === "-s") {
      index += 1;
      parsed.slide = parseSlideNumber(args[index]);
    } else if (arg.startsWith("--slide=")) {
      parsed.slide = parseSlideNumber(arg.slice("--slide=".length));
    } else if (arg === "--auto") {
      index += 1;
      parsed.auto = parseAutoSeconds(args[index]);
    } else if (arg.startsWith("--auto=")) {
      parsed.auto = parseAutoSeconds(arg.slice("--auto=".length));
    } else if (/^\d+$/.test(arg)) {
      parsed.slide = parseSlideNumber(arg);
    } else {
      throw new Error(`Unknown option: ${arg}`);
    }
  }

  return parsed;
}

function parseSlideNumber(value) {
  const number = Number(value);
  if (!Number.isInteger(number) || number < 1 || number > slides.length) {
    throw new Error(`Slide must be an integer from 1 to ${slides.length}.`);
  }
  return number - 1;
}

function parseAutoSeconds(value) {
  const number = Number(value);
  if (!Number.isFinite(number) || number <= 0) {
    throw new Error("--auto expects a positive number of seconds.");
  }
  return number;
}

function startInteractive() {
  process.stdin.setRawMode(true);
  process.stdin.resume();
  process.stdin.setEncoding("utf8");
  process.stdout.write("\u001b[?1049h\u001b[?25l");

  const render = () => {
    process.stdout.write(renderFrame({ mode, index: current, clear: true }));
  };

  const finish = () => {
    if (jumpTimer) clearTimeout(jumpTimer);
    if (autoTimer) clearInterval(autoTimer);
    process.stdin.removeListener("data", onData);
    process.stdout.removeListener("resize", render);
    if (process.stdin.isTTY) process.stdin.setRawMode(false);
    process.stdout.write("\u001b[?25h\u001b[?1049l");
    process.exit(0);
  };

  const onData = (data) => {
    const key = String(data);
    if (key === "\u0003" || key === "q" || key === "Q") {
      finish();
      return;
    }

    if (key === "\u001b" || key === "\u001b[") {
      mode = "slide";
      render();
      return;
    }

    if (key === "\u001b[C" || key === "\u001b[B" || key === "l" || key === "j" || key === " ") {
      current = Math.min(slides.length - 1, current + 1);
      mode = "slide";
      render();
      return;
    }

    if (key === "\u001b[D" || key === "\u001b[A" || key === "h" || key === "k") {
      current = Math.max(0, current - 1);
      mode = "slide";
      render();
      return;
    }

    if (key === "n" || key === "N") {
      mode = mode === "notes" ? "slide" : "notes";
      render();
      return;
    }

    if (key === "o" || key === "O") {
      mode = mode === "overview" ? "slide" : "overview";
      render();
      return;
    }

    if (key === "?") {
      mode = mode === "help" ? "slide" : "help";
      render();
      return;
    }

    if (key === "g") {
      current = 0;
      mode = "slide";
      render();
      return;
    }

    if (key === "G") {
      current = slides.length - 1;
      mode = "slide";
      render();
      return;
    }

    if (/^\d$/.test(key)) {
      pendingJump += key;
      if (jumpTimer) clearTimeout(jumpTimer);
      jumpTimer = setTimeout(() => {
        const number = Number(pendingJump);
        pendingJump = "";
        if (number >= 1 && number <= slides.length) current = number - 1;
        mode = "slide";
        render();
      }, 650);
    }
  };

  process.stdin.on("data", onData);
  process.stdout.on("resize", render);
  process.once("SIGINT", finish);
  process.once("SIGTERM", finish);

  if (options.auto > 0) {
    autoTimer = setInterval(() => {
      if (mode === "slide") {
        current = current === slides.length - 1 ? 0 : current + 1;
        render();
      }
    }, options.auto * 1000);
  }

  render();
}

function renderFrame({ mode: frameMode, index, clear }) {
  const width = terminalWidth();
  const height = terminalHeight();
  const slide = slides[index];
  const header = [
    makeLine("─".repeat(width), { tone: "line" }),
    makeLine(`SCIODYSSEY  /  TERMINAL EDITION    ${slide.chapter}`, { tone: slide.accent, bold: true }),
  ];
  let content;

  if (frameMode === "overview") {
    content = renderOverview(width, index);
  } else if (frameMode === "help") {
    content = renderHelp(width);
  } else if (frameMode === "notes") {
    content = renderNotes(slide, width);
  } else {
    content = renderSlide(slide, width);
  }

  const chromeRows = 5;
  const fitted = fitContent(content, Math.max(4, height - chromeRows), width);
  const footer = [
    makeLine("─".repeat(width), { tone: "line" }),
    makeLine(footerText(frameMode, index, width), { tone: "muted" }),
    makeLine(footerHelp(width), { tone: "dim" }),
  ];

  const lines = [...header, ...fitted, ...footer].map((item) => renderLine(item, width));
  const prefix = clear ? "\u001b[2J\u001b[H" : "";
  return `${prefix}${lines.join("\n")}\n`;
}

function renderSlide(slide, width) {
  const lines = [];
  add(lines, slide.kicker.toUpperCase(), { tone: slide.accent, bold: true });
  add(lines, "");

  const titleLines = Array.isArray(slide.title) ? slide.title : String(slide.title).split("\n");
  for (const title of titleLines) {
    for (const wrapped of wrapText(title, width)) {
      add(lines, wrapped, { tone: "white", bold: true });
    }
  }

  let hasBlock = false;
  for (const block of slide.blocks ?? []) {
    const blockLines = renderBlock(block, width, slide.accent);
    if (!blockLines.length) continue;
    if (hasBlock || lines.at(-1)?.text) add(lines, "");
    lines.push(...blockLines);
    hasBlock = true;
  }
  return lines;
}

function renderBlock(block, width, defaultTone) {
  const tone = block.tone ?? defaultTone;
  switch (block.kind) {
    case "lead":
      return wrapText(block.text, width).map((text) => makeLine(text, { tone: "white", bold: true }));
    case "text":
      return wrapText(block.text, width).map((text) => makeLine(text, { tone }));
    case "quote":
      return String(block.text)
        .split("\n")
        .flatMap((part) => wrapText(part, Math.max(16, width - 8)))
        .map((text) => makeLine(`  “${text}”`, { tone, bold: true, center: true }));
    case "flow":
      return wrapText(flowText(block), width).map((text) => makeLine(text, { tone, bold: true }));
    case "steps":
      return renderGrid(block.items ?? [], width, tone);
    case "timeline":
      return renderTimeline(block.items ?? [], width, tone);
    case "diagram":
    case "tree":
      return (block.lines ?? []).map((text) => makeLine(clip(`  ${text}`, width), { tone }));
    case "table":
      return renderTable(block.headers ?? [], block.rows ?? [], width, tone);
    case "bar": {
      const barWidth = Math.max(10, Math.min(34, width - 42));
      return [
        makeLine(`${block.label.padEnd(10)} ${"█".repeat(Math.floor(barWidth * 0.86))}${"░".repeat(Math.ceil(barWidth * 0.14))}  ${block.value}`, { tone, bold: true }),
        makeLine(`${" ".repeat(10)} ${block.delta}`, { tone: "muted" }),
      ];
    }
    case "metrics":
      return renderGrid((block.items ?? []).map((item) => ({ label: item.value, text: `${item.label}\n${item.detail}`, tone: item.tone ?? tone })), width, tone);
    case "code":
      return (block.lines ?? []).map((text) => makeLine(clip(`  ${text}`, width), { tone: text.startsWith("#") ? "muted" : "green" }));
    case "team":
      return renderTeam(block.items ?? [], width, tone);
    case "callout": {
      const prefix = block.label ? `${block.label}: ` : "";
      return wrapText(`└─ ${prefix}${block.text}`, width).map((text) => makeLine(text, { tone, bold: true }));
    }
    default:
      return [];
  }
}

function renderGrid(items, width, defaultTone) {
  if (!items.length) return [];
  const columns = items.length >= 4 ? 2 : items.length;
  const gap = 3;
  const cellWidth = Math.max(12, Math.floor((width - gap * (columns - 1)) / columns));
  const lines = [];

  for (let start = 0; start < items.length; start += columns) {
    const rowItems = items.slice(start, start + columns);
    const cells = rowItems.map((item) => {
      const label = wrapText(String(item.label ?? ""), cellWidth);
      const text = String(item.text ?? "")
        .split("\n")
        .flatMap((part) => wrapText(part, cellWidth));
      return [...label, ...text];
    });
    const rowHeight = Math.max(...cells.map((cell) => cell.length));
    for (let lineIndex = 0; lineIndex < rowHeight; lineIndex += 1) {
      const row = cells.map((cell) => padRight(cell[lineIndex] ?? "", cellWidth)).join(" ".repeat(gap));
      const rowTone = lineIndex === 0 ? (rowItems[0].tone ?? defaultTone) : "muted";
      lines.push(makeLine(row, { tone: rowTone, bold: lineIndex === 0 }));
    }
  }
  return lines;
}

function renderTimeline(items, width, tone) {
  const labelWidth = 7;
  const textWidth = Math.max(18, width - labelWidth - 5);
  const lines = [];
  for (const item of items) {
    const wrapped = wrapText(item.text, textWidth);
    wrapped.forEach((text, index) => {
      const prefix = index === 0 ? `${String(item.label).padEnd(labelWidth)} > ` : `${" ".repeat(labelWidth)}   `;
      lines.push(makeLine(clip(`${prefix}${text}`, width), { tone: index === 0 ? tone : "muted", bold: index === 0 }));
    });
  }
  return lines;
}

function renderTeam(items, width, tone) {
  const lines = [];
  for (const [initials, name, role, contribution] of items) {
    const head = `[${initials}] ${name}  ${role}`;
    lines.push(makeLine(clip(head, width), { tone, bold: true }));
    lines.push(makeLine(clip(`     ${contribution}`, width), { tone: "muted" }));
  }
  return lines;
}

function renderTable(headers, rows, width, tone) {
  const allRows = [headers, ...rows];
  const columns = headers.length;
  if (!columns) return [];

  const maxWidths = headers.map((_, column) => Math.max(...allRows.map((row) => cellWidth(String(row[column] ?? "")))));
  const minimums = headers.map((header) => Math.min(12, Math.max(5, cellWidth(String(header)))));
  const widths = [...maxWidths];
  const total = () => widths.reduce((sum, value) => sum + value, 0) + (columns - 1) * 3;
  while (total() > width) {
    const candidate = widths.findIndex((value, index) => value > minimums[index]);
    if (candidate === -1) break;
    widths[candidate] -= 1;
  }

  const lines = [];
  allRows.forEach((row, rowIndex) => {
    const rendered = row.map((value, column) => padRight(clip(String(value ?? ""), widths[column]), widths[column]));
    lines.push(makeLine(rendered.join("   "), { tone: rowIndex === 0 ? tone : rowIndex === allRows.length - 1 ? "green" : "muted", bold: rowIndex === 0 || rowIndex === allRows.length - 1 }));
    if (rowIndex === 0) {
      lines.push(makeLine(widths.map((value) => "─".repeat(value)).join("───"), { tone: "line" }));
    }
  });
  return lines;
}

function renderOverview(width, currentIndex) {
  const lines = [
    makeLine("SLIDE INDEX", { tone: "white", bold: true }),
    makeLine("Choose a slide with number keys, then wait briefly.", { tone: "muted" }),
    makeLine(""),
  ];
  const columns = 2;
  const gap = 4;
  const columnWidth = Math.max(16, Math.floor((width - gap) / columns));
  for (let start = 0; start < slides.length; start += columns) {
    const cells = [];
    for (let offset = 0; offset < columns; offset += 1) {
      const index = start + offset;
      if (index >= slides.length) {
        cells.push("".padEnd(columnWidth));
        continue;
      }
      const marker = index === currentIndex ? ">" : " ";
      const title = Array.isArray(slides[index].title) ? slides[index].title.join(" ") : slides[index].title;
      cells.push(padRight(clip(`${marker} ${String(index + 1).padStart(2, "0")}  ${title}`, columnWidth), columnWidth));
    }
    lines.push(makeLine(cells.join(" ".repeat(gap)), { tone: "muted" }));
  }
  return lines;
}

function renderHelp(width) {
  const entries = [
    ["← / h / k", "previous slide"],
    ["→ / j / l / space", "next slide"],
    ["1–24", "jump to a slide"],
    ["n", "toggle speaker notes"],
    ["o", "toggle slide outline"],
    ["g / G", "first / last slide"],
    ["?", "toggle this help"],
    ["q / Ctrl-C", "quit"],
  ];
  const lines = [makeLine("KEYBOARD", { tone: "white", bold: true }), makeLine("")];
  for (const [key, action] of entries) {
    lines.push(makeLine(`${key.padEnd(20)} ${action}`, { tone: "muted" }));
  }
  return lines;
}

function renderNotes(slide, width) {
  const lines = [
    makeLine("SPEAKER NOTES", { tone: "white", bold: true }),
    makeLine(""),
    makeLine(Array.isArray(slide.title) ? slide.title.join(" ") : slide.title, { tone: slide.accent, bold: true }),
    makeLine(""),
  ];
  lines.push(...wrapText(slide.note ?? "No notes for this slide.", width).map((text) => makeLine(text, { tone: "muted" })));
  return lines;
}

function fitContent(lines, maxRows, width) {
  let fitted = lines.map((item) => (typeof item === "string" ? makeLine(item) : item));
  while (fitted.length > maxRows && fitted.some((item) => !item.text)) {
    fitted = fitted.filter((item, index) => item.text || index === 0);
  }
  if (fitted.length <= maxRows) return fitted;
  const clipped = fitted.slice(0, Math.max(1, maxRows - 1));
  clipped.push(makeLine(clip("… resize terminal or use --print for the full slide", width), { tone: "dim" }));
  return clipped;
}

function footerText(frameMode, index, width) {
  if (frameMode === "overview") return clip(`OUTLINE  /  current slide ${index + 1} of ${slides.length}`, width);
  if (frameMode === "help") return clip("HELP  /  press ? or Esc to return", width);
  if (frameMode === "notes") return clip(`NOTES  /  slide ${index + 1} of ${slides.length}`, width);
  const title = Array.isArray(slides[index].title) ? slides[index].title.join(" ") : slides[index].title;
  return clip(`SLIDE ${String(index + 1).padStart(2, "0")} / ${String(slides.length).padStart(2, "0")}  ${title}`, width);
}

function footerHelp(width) {
  return clip("←/→ navigate   n notes   o outline   ? help   q quit", width);
}

function runLayoutCheck() {
  const samples = [
    { columns: 80, rows: 24 },
    { columns: 120, rows: 36 },
  ];
  let failed = false;
  for (const sample of samples) {
    const width = Math.max(24, sample.columns - 2);
    const maxRows = Math.max(4, sample.rows - 5);
    const overflows = [];
    for (const [index, slide] of slides.entries()) {
      const content = renderSlide(slide, width);
      const fitted = fitContent(content, maxRows, width);
      if (fitted.at(-1)?.text.startsWith("…")) overflows.push(index + 1);
    }
    const status = overflows.length ? `WARN slides ${overflows.join(", ")}` : "OK";
    if (overflows.length) failed = true;
    console.log(`${sample.columns}x${sample.rows}: ${status}`);
  }
  if (failed) process.exitCode = 1;
}

function printOutline() {
  for (const [index, slide] of slides.entries()) {
    const title = Array.isArray(slide.title) ? slide.title.join(" ") : slide.title;
    console.log(`${String(index + 1).padStart(2, "0")}  ${slide.chapter.padEnd(18)}  ${title}`);
  }
}

function printHelp() {
  console.log(`SciOdyssey terminal edition

Usage:
  node terminal/present.mjs                 interactive presentation
  node terminal/present.mjs --slide 15     start at slide 15
  node terminal/present.mjs --print 15     print one slide and exit
  node terminal/present.mjs --list         print the slide outline
  node terminal/present.mjs --check        check the 80x24 and 120x36 layouts
  node terminal/present.mjs --auto 8       advance every 8 seconds
  node terminal/present.mjs --no-color     disable ANSI colors

Inside the presentation:
  arrows / h j k l / space  navigate
  n                         speaker notes
  o                         slide outline
  1–24                      jump to a slide
  ?                         help
  q                         quit`);
}

function add(lines, text, options = {}) {
  lines.push(makeLine(text, options));
}

function makeLine(text, options = {}) {
  return { text: String(text ?? ""), ...options };
}

function renderLine(item, width) {
  const text = item.center ? centerText(clip(item.text, width), width) : padRight(clip(item.text, width), width);
  return style(text, item.tone, item);
}

function flowText(block) {
  const items = block.items.map((item) => `[${item}]`).join("  >  ");
  return block.label ? `${block.label}  ${items}` : items;
}

function wrapText(value, width) {
  const safeWidth = Math.max(1, width);
  const paragraphs = String(value ?? "").replaceAll("\r", "").split("\n");
  const result = [];
  for (const paragraph of paragraphs) {
    if (!paragraph.trim()) {
      result.push("");
      continue;
    }
    let line = "";
    for (const word of paragraph.trim().split(/\s+/)) {
      if (!line) {
        if (cellWidth(word) <= safeWidth) {
          line = word;
        } else {
          const parts = breakLongWord(word, safeWidth);
          result.push(...parts.slice(0, -1));
          line = parts.at(-1) ?? "";
        }
      } else if (cellWidth(`${line} ${word}`) <= safeWidth) {
        line += ` ${word}`;
      } else {
        result.push(line);
        if (cellWidth(word) <= safeWidth) {
          line = word;
        } else {
          const parts = breakLongWord(word, safeWidth);
          result.push(...parts.slice(0, -1));
          line = parts.at(-1) ?? "";
        }
      }
    }
    if (line) result.push(line);
  }
  return result;
}

function breakLongWord(word, width) {
  const parts = [];
  let part = "";
  for (const character of Array.from(word)) {
    if (cellWidth(`${part}${character}`) > width && part) {
      parts.push(part);
      part = character;
    } else {
      part += character;
    }
  }
  if (part) parts.push(part);
  return parts;
}

function clip(value, width) {
  if (cellWidth(value) <= width) return value;
  const suffix = width > 1 ? "…" : "";
  let output = "";
  for (const character of Array.from(value)) {
    if (cellWidth(`${output}${character}${suffix}`) > width) break;
    output += character;
  }
  return `${output}${suffix}`;
}

function padRight(value, width) {
  return `${value}${" ".repeat(Math.max(0, width - cellWidth(value)))}`;
}

function centerText(value, width) {
  const left = Math.max(0, Math.floor((width - cellWidth(value)) / 2));
  return `${" ".repeat(left)}${value}${" ".repeat(Math.max(0, width - left - cellWidth(value)))}`;
}

function cellWidth(value) {
  let width = 0;
  for (const character of Array.from(stripAnsi(String(value)))) {
    const code = character.codePointAt(0);
    if (code === undefined || /\p{Mark}/u.test(character)) continue;
    if ((code >= 0x1100 && code <= 0x11ff) || (code >= 0x2e80 && code <= 0xa4cf) || (code >= 0xac00 && code <= 0xd7af) || (code >= 0xf900 && code <= 0xfaff) || (code >= 0xfe10 && code <= 0xfe6f) || (code >= 0xff00 && code <= 0xffef) || code >= 0x1f300) {
      width += 2;
    } else {
      width += 1;
    }
  }
  return width;
}

function stripAnsi(value) {
  return value.replace(/\u001b\[[0-?]*[ -/]*[@-~]/g, "");
}

function style(text, tone = "white", options = {}) {
  if (!useColor) return text;
  const rgb = palette[tone] ?? palette.white;
  const codes = [`38;2;${rgb[0]};${rgb[1]};${rgb[2]}`];
  if (options.bold) codes.unshift("1");
  if (options.dim) codes.unshift("2");
  return `\u001b[${codes.join(";")}m${text}\u001b[0m`;
}

function terminalWidth() {
  return Math.max(24, Math.min(112, (process.stdout.columns || 96) - 2));
}

function terminalHeight() {
  return Math.max(10, process.stdout.rows || 30);
}

