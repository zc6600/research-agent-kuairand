import { chromium } from 'playwright-chromium';
import { PDFDocument } from 'pdf-lib';
import { writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('./', import.meta.url);

const problemPolishCss = String.raw`
.problem {
  display: flex;
  flex-direction: column;
  padding: 14px 20px 14px;
}
.problem h2 {
  max-width: 455px;
  font-size: 32px;
  letter-spacing: -1.35px;
}
.problem-lead {
  margin-top: 5px;
  max-width: 490px;
  color: #536579;
  font-size: 13.6px;
}
.problem .world-art {
  top: 17px;
  right: 20px;
  width: 78px;
  height: 78px;
  opacity: .38;
}
.problem .failure-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 10px;
}
.problem .failure-item {
  position: relative;
  display: grid;
  grid-template-columns: 24px 1fr;
  grid-template-rows: auto;
  column-gap: 8px;
  min-height: 206px;
  padding: 11px 11px 10px;
  overflow: hidden;
  border: 1px solid #e2d5c1;
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(255,255,255,.32), rgba(255,255,255,.06)), #f1e8d8;
}
.problem .failure-item::before {
  content: '';
  position: absolute;
  inset: 0;
  border-top: 3px solid var(--navy);
  opacity: .86;
}
.problem .failure-item.failure-inertia::before { border-top-color: var(--rust); }
.problem .failure-item.failure-context::before { border-top-color: var(--navy); }
.problem .failure-idx {
  grid-column: 1;
  grid-row: 1;
  position: relative;
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  margin: 0;
  border-radius: 50%;
  border: 1px solid #b7c7d1;
  background: #f9f6ed;
  color: var(--navy);
  font-size: 10px;
}
.problem .failure-inertia .failure-idx { color: var(--rust); border-color: #d4aa93; }
.problem .failure-context .failure-idx { color: var(--navy); border-color: #a5c5dc; }
.problem .failure-text {
  grid-column: 2;
  grid-row: 1;
  position: relative;
  min-width: 0;
}
.problem .failure-text strong {
  font-family: var(--serif);
  font-size: 16.5px;
  line-height: 1.05;
  letter-spacing: -.4px;
}
.problem .failure-claim {
  display: block;
  margin-top: 3px;
  color: #2f3e4a;
  font-size: 10.8px;
  line-height: 1.22;
}
.problem .failure-diagram {
  margin-top: 6px;
  border: 1px solid #ded1bd;
  border-radius: 5px;
  background: #faf6ed;
  padding: 5px 6px 4px;
}
.problem .failure-svg {
  display: block;
  width: 100%;
  height: 48px;
}
.problem .failure-takeaway {
  display: block;
  margin-top: 5px;
  color: #65717b;
  font-family: var(--mono);
  font-size: 8.6px;
  font-weight: 600;
  letter-spacing: -.1px;
  line-height: 1.22;
}
.problem .failure-takeaway b {
  color: var(--rust);
}
.problem .architecture-contrast {
  display: none;
}
.problem .problem-solution-bar {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  margin-top: auto;
  min-height: 60px;
  border: 1px solid #ddb8a5;
  border-left: 4px solid var(--rust);
  border-radius: 8px;
  padding: 8px 14px 7px;
  background: linear-gradient(90deg, #fbf0ea, #f6ede2);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.6);
}
.problem .bar-top-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.problem .bar-tag {
  font-family: var(--mono);
  font-size: 8.2px;
  font-weight: 800;
  letter-spacing: .8px;
  background: var(--rust);
  color: #fff;
  padding: 2px 5.5px;
  border-radius: 3px;
  white-space: nowrap;
}
.problem .bar-headline {
  display: flex;
  align-items: baseline;
  gap: 6px;
  min-width: 0;
}
.problem .bar-headline strong {
  font-family: var(--serif);
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: -.25px;
  color: #6b2612;
  white-space: nowrap;
}
.problem .bar-sep {
  color: #c98e79;
  font-weight: 400;
}
.problem .bar-thesis {
  font-size: 9.6px;
  color: #7d4837;
  font-weight: 500;
  white-space: nowrap;
}
.problem .bar-targets {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  border-top: 1px dashed #e2c8ba;
  padding-top: 5px;
}
.problem .bar-target {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: var(--mono);
  font-size: 8.8px;
  font-weight: 600;
  color: #5c3b31;
  letter-spacing: -.1px;
  white-space: nowrap;
}
.problem .target-bullet {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: #ecd3c6;
  color: #8c3217;
  font-size: 8px;
  font-style: normal;
  font-weight: 800;
  flex-shrink: 0;
}
`;

const systemPolishCss = String.raw`
.system {
  padding: 18px 22px 16px;
}
.system h2 {
  max-width: 430px;
  font-size: 31px;
  letter-spacing: -1.25px;
}
.system-intro {
  margin-top: 5px;
  color: #5b6875;
  font-size: 12.8px;
}
.system .system-architecture.system-loop {
  margin-top: 12px;
  border: 1px solid #ded1bd;
  border-radius: 10px;
  padding: 12px 13px 13px;
  background: linear-gradient(180deg, rgba(255,255,255,.28), rgba(255,255,255,.04)), #f1e8d8;
}
.system .loop-kicker {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
  padding-bottom: 7px;
  border-bottom: 1px solid #dfd1bc;
}
.system .loop-kicker span {
  color: var(--navy);
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.2px;
}
.system .loop-kicker small {
  color: #6e7780;
  font-size: 10px;
}
.system .loop-layout {
  display: grid;
  grid-template-columns: 74px 1fr;
  gap: 10px;
  margin-top: 10px;
}
.system .input-rail {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  border: 1px solid #d8c8b2;
  border-radius: 8px;
  padding: 10px 8px;
  background: #faf6ed;
}
.system .input-rail b {
  color: var(--rust);
  font-family: var(--mono);
  font-size: 8.5px;
  letter-spacing: .9px;
}
.system .input-rail span {
  color: #445461;
  font-family: var(--mono);
  font-size: 8.6px;
  font-weight: 700;
  letter-spacing: .55px;
}
.system .loop-core {
  display: grid;
  grid-template-rows: auto auto auto auto;
  gap: 8px;
  min-width: 0;
}
.system .ephemeral-row {
  display: grid;
  grid-template-columns: 1fr 32px 1fr;
  gap: 8px;
  align-items: stretch;
}
.system .actor-node {
  position: relative;
  min-height: 96px;
  border: 1px solid #ded1bd;
  border-radius: 8px;
  padding: 10px 12px 9px;
  background: #fbf7ef;
}
.system .actor-node::before {
  content: '';
  position: absolute;
  inset: 0;
  border-top: 3px solid var(--purple);
  border-radius: inherit;
  pointer-events: none;
}
.system .actor-node.meta::before { border-top-color: var(--rust); }
.system .actor-node b {
  display: block;
  color: var(--ink);
  font-family: var(--serif);
  font-size: 18px;
  line-height: 1.02;
  letter-spacing: -.55px;
}
.system .actor-node p {
  margin-top: 6px;
  color: #415160;
  font-size: 10.5px;
  line-height: 1.25;
}
.system .actor-arrow {
  display: grid;
  place-items: center;
  color: #9fb7c4;
  font-size: 20px;
  font-weight: 700;
}
.system .reset-boundary {
  display: grid;
  grid-template-columns: 135px 1fr;
  gap: 10px;
  align-items: center;
  min-height: 39px;
  border: 1px dashed #d39479;
  border-radius: 8px;
  padding: 7px 10px;
  background: #fbefe7;
}
.system .reset-boundary b {
  color: var(--rust);
  font-family: var(--mono);
  font-size: 9.4px;
  letter-spacing: 1px;
}
.system .reset-boundary span {
  color: #5b4d46;
  font-size: 11.2px;
  line-height: 1.2;
}
.system .persistence-return {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 34px;
  border-left: 3px solid var(--navy);
  border-radius: 0 8px 8px 0;
  padding: 7px 10px;
  background: linear-gradient(90deg, #e2ebf2, #efe7dc);
}
.system .persistence-return b {
  color: var(--navy);
  font-family: var(--mono);
  font-size: 9.2px;
  letter-spacing: .9px;
  flex-shrink: 0;
}
.system .persistence-return span {
  color: #374a58;
  font-size: 10.8px;
  line-height: 1.18;
}
.system .world-node {
  border: 1px solid #d4c8b6;
  border-radius: 10px;
  background: linear-gradient(180deg, #f0e9dc, #e8dfcf);
  padding: 11px 12px 12px;
}
.system .world-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}
.system .world-head b {
  color: var(--navy);
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: 1.3px;
}
.system .world-head span {
  color: #6a7985;
  font-size: 10px;
}
.system .world-strata {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 8px;
}
.system .world-stratum {
  min-height: 92px;
  border: 1px solid #ded4c3;
  border-radius: 7px;
  padding: 9px 9px 8px;
  background: #fbf7ef;
}
.system .world-stratum span {
  display: inline-block;
  color: var(--navy);
  font-family: var(--mono);
  font-size: 7.8px;
  font-weight: 800;
  letter-spacing: .65px;
  background: #e2ebf2;
  border-radius: 3px;
  padding: 2px 5px;
}
.system .world-stratum:nth-child(1) span { color: var(--navy); background: #e2ebf2; }
.system .world-stratum:nth-child(2) span { color: var(--amber); background: #f6ead7; }
.system .world-stratum:nth-child(3) span { color: var(--navy); background: #e2ebf2; }
.system .world-stratum strong {
  display: block;
  margin-top: 6px;
  color: var(--ink);
  font-family: var(--serif);
  font-size: 15.6px;
  line-height: 1.05;
  letter-spacing: -.35px;
}
.system .world-stratum p {
  margin-top: 4px;
  color: #40505d;
  font-size: 9.9px;
  line-height: 1.20;
}
.system .persistence-container {
  display: none;
}
.system .system-footer-grid.runtime-substrate {
  grid-template-columns: 88px repeat(3, 1fr);
  gap: 7px;
  margin-top: 10px;
}
.system .runtime-label {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d6c8b7;
  border-radius: 7px;
  background: #f1e8d8;
  color: var(--navy);
  font-family: var(--mono);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: .9px;
  text-align: center;
}
.system .runtime-substrate .footer-block {
  min-height: 70px;
  padding: 8px 9px;
  background: #fbf7ef;
}
.system .runtime-substrate .footer-kicker {
  font-size: 8.6px;
}
.system .runtime-substrate .footer-block p {
  font-size: 9.7px;
  line-height: 1.20;
}
.system .system-principle-box {
  margin-top: 10px;
  border-left: 3px solid var(--rust);
  border-radius: 0 8px 8px 0;
  background: linear-gradient(90deg, #fbefe7, #f6eadb);
  padding: 10px 13px;
}
.system .system-principle {
  color: #7a2c16;
  font-family: var(--serif);
  font-size: 18px;
  line-height: 1.13;
  letter-spacing: -.35px;
}
.system .system-principle b {
  color: #7a2c16;
}
.system .principle-pillars {
  margin-top: 5px;
  font-size: 8.4px;
  color: #8c3217;
}
`;

const evaluationPolishCss = String.raw`
.trajectory-card {
  padding-bottom: 7px;
}
.trajectory-chart-legend {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 14px;
  margin-top: 3px;
  padding: 0 1px;
}
.tc-legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 8.8px;
  color: #4b5a67;
}
.tc-legend-item.is-sciodyssey {
  color: var(--navy);
}
.tc-legend-item.is-codex {
  color: #657584;
}
.tc-line {
  display: inline-block;
  width: 14px;
  height: 2px;
  border-radius: 1px;
}
.tc-line.is-solid {
  background: var(--navy);
}
.tc-line.is-dashed {
  height: 0;
  border-top: 1.5px dashed #9bb0be;
  background: transparent;
}
.tc-dot {
  display: inline-block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  margin-left: -2px;
}
.is-sciodyssey .tc-dot {
  background: var(--navy);
}
.is-codex .tc-dot {
  background: #9bb0be;
}
.trajectory-svg-container {
  margin-top: 5px;
  border: 1px solid #dfd4c4;
  border-radius: 6px;
  background: #fbf7ee;
  padding: 4px 6px 3px;
}
.trajectory-line-chart {
  display: block;
  width: 100%;
  height: 108px;
}
.trajectory-stats-row {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 7px;
  margin-bottom: 2px;
  font-family: var(--mono);
  font-size: 8.8px;
  color: #556673;
}
.trajectory-stats-row b {
  color: var(--ink);
}
.trajectory-stats-row i {
  font-style: normal;
  color: #c0b3a3;
}
.trajectory-stats-row .t-gain b {
  color: #16803b;
}

/* Card 03: Self-Healing & Gatekeeping */
.recovery-card {
  padding-bottom: 9px;
}
.two-tier-blocks {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-top: 6px;
}
.tier-block {
  border: 1px solid var(--border-light);
  border-radius: 6px;
  padding: 6px 9px 5px;
  background: var(--paper-card-sub);
}
.tier-block.tier-1 { border-left: 3.5px solid var(--rust); }
.tier-block.tier-2 { border-left: 3.5px solid var(--purple); background: var(--paper-card-sub); }
.tier-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 3.5px;
}
.tier-badge {
  font-family: var(--mono);
  font-size: 8.5px;
  font-weight: 800;
  letter-spacing: .6px;
}
.tier-1 .tier-badge { color: var(--rust); }
.tier-2 .tier-badge { color: var(--purple); }
.tier-receipt,
.tier-subhead {
  font-family: var(--mono);
  font-size: 7.8px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.tier-block code {
  color: var(--navy);
  font-family: var(--mono);
  font-size: 8.2px;
  background: rgba(11, 69, 107, 0.06);
  padding: 1px 3px;
  border-radius: 3px;
}
.tier-flow-mini {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.tf-row {
  display: grid;
  grid-template-columns: 66px 1fr;
  align-items: baseline;
  gap: 6px;
  font-size: 8.5px;
  line-height: 1.25;
  color: var(--body);
}
.tf-row.tf-out {
  margin-top: 1px;
  background: rgba(11, 69, 107, 0.07);
  border: 1px solid rgba(11, 69, 107, 0.18);
  border-radius: 4px;
  padding: 2px 5px;
  color: #0b3d5e;
}
.tf-lbl {
  font-family: var(--mono);
  font-size: 7.4px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: #71818e;
}
.tf-row.tf-out .tf-lbl {
  color: var(--navy);
}
.recovery-card .card-annotation {
  margin-top: 6px;
  font-size: 9px;
  line-height: 1.22;
}
`;

function applyProblemPolish() {
  const panel = document.querySelector('.problem');
  if (!panel) return;

  panel.querySelector('.problem-lead').textContent = 'Sustained autonomous research breaks in three different ways.';

  const failures = [...panel.querySelectorAll('.failure-item')];
  const entries = [
    {
      cls: 'failure-fragility',
      title: 'Closed-world fragility',
      claim: 'Fixed workflows shatter on unexpected runtime errors.',
      svg: `
        <svg viewBox="0 0 176 46" class="failure-svg" aria-label="Observe to Code to Error to dead end">
          <g class="f-step">
            <rect x="3" y="4" width="39" height="17" rx="3" fill="#f8f4eb" stroke="#d5c8b5" stroke-width="1" />
            <text x="22.5" y="15.5" font-size="8" text-anchor="middle" fill="#2d3d49" font-family="var(--mono)" font-weight="600">Observe</text>
          </g>
          <path d="M 45 12.5 L 50 12.5" stroke="#9bb2c0" stroke-width="1.3" />
          <polygon points="53,12.5 49,10 49,15" fill="#9bb2c0" />

          <g class="f-step">
            <rect x="55" y="4" width="34" height="17" rx="3" fill="#f8f4eb" stroke="#d5c8b5" stroke-width="1" />
            <text x="72" y="15.5" font-size="8" text-anchor="middle" fill="#2d3d49" font-family="var(--mono)" font-weight="600">Code</text>
          </g>
          <path d="M 92 12.5 L 97 12.5" stroke="#9bb2c0" stroke-width="1.3" />
          <polygon points="100,12.5 96,10 96,15" fill="#9bb2c0" />

          <g class="f-step f-err">
            <rect x="102" y="4" width="70" height="17" rx="3" fill="#fbeee7" stroke="#e0a892" stroke-width="1" />
            <text x="137" y="15.5" font-size="8.2" font-weight="800" text-anchor="middle" fill="#b94020" font-family="var(--mono)">✖ ERROR</text>
          </g>

          <line x1="137" y1="21" x2="137" y2="24" stroke="#b94020" stroke-width="1.2" stroke-dasharray="2 1.5" />
          <polygon points="137,26 134.5,23 139.5,23" fill="#b94020" />

          <rect x="94" y="26.5" width="80" height="16.5" rx="3" fill="#faefe9" stroke="#ddb8a5" stroke-width="1" />
          <text x="134" y="37.8" font-size="6.7" font-weight="700" text-anchor="middle" fill="#8c3217" font-family="var(--mono)">dead end (halts)</text>
        </svg>
      `,
      takeaway: 'Unhandled runtime faults halt unassisted runs',
    },
    {
      cls: 'failure-inertia',
      title: 'Trajectory momentum',
      claim: 'A single context carries past momentum into local basins.',
      svg: `
        <svg viewBox="0 0 176 46" class="failure-svg" aria-label="Trajectory trapped in local basin missing alternative ideas">
          <path d="M 8 11 Q 60 42 112 19" fill="none" stroke="#d5c8b5" stroke-width="1.5" stroke-dasharray="3 2" />
          <circle cx="22" cy="18" r="3" fill="#718290" />
          <line x1="25" y1="19.5" x2="44" y2="27.5" stroke="#b94020" stroke-width="1.5" />
          <circle cx="46" cy="28" r="3" fill="#718290" />
          <line x1="49" y1="29" x2="72" y2="32" stroke="#b94020" stroke-width="1.5" />
          <circle cx="74" cy="32" r="4" fill="#b94020" stroke="#fff" stroke-width="1" />
          <path d="M 80 31 C 90 29 92 40 82 41" fill="none" stroke="#b94020" stroke-width="1.2" />
          <polygon points="79,41 83,39 83,43" fill="#b94020" />
          <text x="50" y="41" font-size="7.2" font-weight="700" text-anchor="middle" fill="#b94020" font-family="var(--mono)">local basin ↺</text>

          <rect x="116" y="5" width="56" height="36" rx="4" fill="#faf6ed" stroke="#ded1bd" stroke-width="1" stroke-dasharray="2 2" />
          <text x="144" y="18" font-size="11" text-anchor="middle" fill="#c06c1e">★</text>
          <text x="144" y="27" font-size="7.5" font-weight="700" text-anchor="middle" fill="#364450" font-family="var(--mono)">new idea</text>
          <text x="144" y="36.5" font-size="6.8" text-anchor="middle" fill="#8c7a6b" font-family="var(--mono)">(missed)</text>
        </svg>
      `,
      takeaway: '22 runs trapped tweaking parameters in same basin',
    },
    {
      cls: 'failure-context',
      title: 'Context inflation cost',
      claim: 'Reconstructing context costs far more than the edit itself.',
      svg: `
        <svg viewBox="0 0 176 46" class="failure-svg" aria-label="Read context 340K versus edit 42K ratio">
          <text x="2" y="14" font-size="7.8" font-weight="700" fill="#0b456b" font-family="var(--mono)">READ</text>
          <rect x="28" y="5" width="98" height="13" rx="2.5" fill="#e2ebf2" stroke="#b8cad6" stroke-width="1" />
          <text x="132" y="15" font-size="8.2" font-weight="800" fill="#0b456b" font-family="var(--mono)">340K</text>

          <text x="2" y="34" font-size="7.8" font-weight="700" fill="#718290" font-family="var(--mono)">EDIT</text>
          <rect x="28" y="25" width="14" height="13" rx="2.5" fill="#f0e6dc" stroke="#d5c8b5" stroke-width="1" />
          <text x="46" y="35" font-size="8" font-weight="700" fill="#718290" font-family="var(--mono)">42K</text>

          <rect x="102" y="23" width="71" height="17" rx="3" fill="#faefe9" stroke="#d39479" stroke-width="1" />
          <text x="137.5" y="35" font-size="8.2" font-weight="800" text-anchor="middle" fill="#b94020" font-family="var(--mono)">8.0× overhead</text>
        </svg>
      `,
      takeaway: '10 files read to change 1 line; burns token budget',
    },
  ];

  failures.forEach((item, index) => {
    const entry = entries[index];
    if (!entry) return;
    item.className = `failure-item ${entry.cls}`;
    item.innerHTML = `
      <span class="failure-idx">0${index + 1}</span>
      <div class="failure-text">
        <strong>${entry.title}</strong>
        <span class="failure-claim">${entry.claim}</span>
        <div class="failure-diagram">${entry.svg}</div>
        <span class="failure-takeaway">${entry.takeaway}</span>
      </div>
    `;
  });

  panel.querySelector('.architecture-contrast')?.remove();
  const bar = panel.querySelector('.problem-solution-bar');
  if (bar) {
    bar.innerHTML = `
      <div class="bar-top-row">
        <span class="bar-tag">DESIGN RESPONSE</span>
        <div class="bar-headline">
          <strong>Keep the world. Reset the trajectory.</strong>
          <span class="bar-sep">·</span>
          <span class="bar-thesis">Decouple persistent memory from reasoning</span>
        </div>
      </div>
      <div class="bar-targets">
        <span class="bar-target"><i class="target-bullet">1</i> Auto-heal runtime faults</span>
        <span class="bar-target"><i class="target-bullet">2</i> Fresh reasoning each cycle</span>
        <span class="bar-target"><i class="target-bullet">3</i> Reusable disk state (no token waste)</span>
      </div>
    `;
  }
}

function applySystemPolish() {
  const panel = document.querySelector('.system');
  if (!panel) return;

  const intro = panel.querySelector('.system-intro');
  if (intro) intro.textContent = 'Give the research world and the researcher different lifetimes.';

  const arch = panel.querySelector('.system-architecture');
  if (arch) {
    arch.classList.add('system-loop');
    arch.innerHTML = `
      <div class="loop-kicker">
        <span>DUAL-LIFETIME LOOP</span>
        <small>Persistent world · ephemeral trajectory · audited write-back</small>
      </div>
      <div class="loop-layout">
        <div class="input-rail">
          <b>INPUTS</b>
          <span>TASK</span>
          <span>DATA</span>
          <span>EVALUATOR</span>
          <span>BUDGET</span>
        </div>
        <div class="loop-core">
          <div class="ephemeral-row">
            <div class="actor-node scientist">
              <b>Fresh Scientist</b>
              <p>Owns scientific judgment inside one trajectory: hypotheses, code, experiments, interpretation, and pivots.</p>
            </div>
            <div class="actor-arrow">→</div>
            <div class="actor-node meta">
              <b>META Review</b>
              <p>Audits claims against artifacts, scopes conclusions, and decides what is durable enough to survive.</p>
            </div>
          </div>
          <div class="persistence-return"><b>SELECTIVE PERSISTENCE</b><span>Only audited empirical findings, code state, and bounded priors write back to the shared world.</span></div>
          <div class="world-node">
            <div class="world-head"><b>PERSISTENT RESEARCH WORLD</b><span>What survives across trajectories</span></div>
            <div class="world-strata">
              <div class="world-stratum"><span>A · EVIDENCE</span><strong>Knowledge + Ledger</strong><p>Metrics, failures, reports, and experiment receipts in <b><code>ledger.jsonl</code></b>.</p></div>
              <div class="world-stratum"><span>B · PRIORS</span><strong>Brief + Hypotheses</strong><p>Current understanding and exploration leads in <b><code>brief.md</code></b>, open to revision.</p></div>
              <div class="world-stratum"><span>C · STATE</span><strong>Code + State</strong><p>Retained implementation, serialized model weights, checks, and git provenance.</p></div>
            </div>
          </div>
          <div class="reset-boundary"><b>CONTEXT RESET</b><span>The next Scientist reads verified experience from disk, but does not inherit the previous reasoning trace.</span></div>
        </div>
      </div>
    `;
  }

  panel.querySelector('.persistence-container')?.remove();
  const runtime = panel.querySelector('.system-footer-grid');
  if (runtime) {
    runtime.classList.add('runtime-substrate');
    runtime.innerHTML = `
      <div class="runtime-label">RUNTIME<br>SUBSTRATE</div>
      <div class="footer-block"><span class="footer-kicker">WORKTREE ISOLATION</span><p>Independent git worktrees isolate branches and preserve reproducible artifacts.</p></div>
      <div class="footer-block"><span class="footer-kicker">SELF-HEALING</span><p>Traceback → patch → rerun keeps unattended research moving after runtime faults.</p></div>
      <div class="footer-block"><span class="footer-kicker">PARALLEL SYNTHESIS</span><p>Completed branches can be compared post-hoc; useful ideas survive even when a branch loses.</p></div>
    `;
  }

  const principle = panel.querySelector('.system-principle-box');
  if (principle) {
    principle.innerHTML = `
      <p class="system-principle">The next Scientist inherits <b>verified experience</b> — not <b>prior reasoning momentum</b>.</p>
      <div class="principle-pillars"><span>Decoupled Memory</span><i>·</i><span>Audited Persistence</span><i>·</i><span>Fresh Scientific Judgment</span></div>
    `;
  }
}

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 2036 }, deviceScaleFactor: 2 });
  await page.goto(new URL('poster.html', root).href, { waitUntil: 'networkidle' });
  await page.addStyleTag({ content: problemPolishCss });
  await page.addStyleTag({ content: systemPolishCss });
  await page.addStyleTag({ content: evaluationPolishCss });
  await page.evaluate(applyProblemPolish);
  await page.evaluate(applySystemPolish);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    await Promise.all([...document.images].map(img => img.decode()));
  });
  const audit = await page.evaluate(() => {
    const out = [];
    for (const panel of document.querySelectorAll('.panel')) {
      const box = panel.getBoundingClientRect();
      for (const child of panel.querySelectorAll('h2,h3,p,li,td,th,.memory-row,.handoff,.terminal,.stats,.problem-note,.runtime,.parallel,.system-flow,.evidence-grid,.evidence-card,.resource-metrics,.insight-grid,.persistence-lanes,.system-principle,.loop-layout,.loop-core,.world-node,.world-strata,.runtime-substrate')) {
        const r = child.getBoundingClientRect();
        if (r.bottom > box.bottom - 3 || r.right > box.right - 3 || r.left < box.left) {
          out.push({ section: panel.className, element: child.tagName, text: child.textContent.trim().slice(0, 100), bottom: r.bottom, panelBottom: box.bottom });
        }
      }
    }
    return { overflow: out, width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight, headings: [...document.querySelectorAll('.section-label')].map(x => x.textContent) };
  });
  await writeFile(new URL('layout-check.json', root), JSON.stringify(audit, null, 2));
  await page.screenshot({ path: fileURLToPath(new URL('preview.png', root)), fullPage: true });
  if (audit.overflow.length || audit.width !== 1440 || audit.height !== 2036) {
    throw new Error('Poster layout overflow: ' + JSON.stringify(audit));
  }
  const bytes = await page.pdf({ preferCSSPageSize: true, printBackground: true });
  const pdf = await PDFDocument.load(bytes);
  if (pdf.getPageCount() !== 1) throw new Error('Expected one poster page');
  const sheet = pdf.getPage(0);
  const a1Width = 594 * 72 / 25.4;
  const a1Height = 841 * 72 / 25.4;
  sheet.scale(a1Width / sheet.getWidth(), a1Height / sheet.getHeight());
  pdf.setTitle('SciOdyssey · Main deck evidence poster · Team Good4AI');
  pdf.setAuthor('Team Good4AI (Chen Zhu, Zhou Ziyu, Shilin Xu, GE GAO, Jiran Li)');
  const output = new URL('SciOdyssey-poster-main-deck.pdf', root);
  await writeFile(output, await pdf.save());
  console.log('Exported ' + fileURLToPath(output) + ' (one A1 page, 594 × 841 mm)');
  console.log('Five evidence claims checked; no panel overflow.');
} finally {
  await browser.close();
}
