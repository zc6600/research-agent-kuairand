import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Dot, FileToken, MicroLabel, Surface, Terminal, Trace, V2World} from '../v2-components';
import {V2C, camera, fadeInOut, p} from '../v2-motion';

export const V2ResumeScene: React.FC = () => {
  const frame = useCurrentFrame();
  const restore = p(frame, 82, 238);
  const world = p(frame, 176, 250);
  const darkness = 1 - p(frame, 0, 24);
  return (
    <Surface tone="light">
      <AbsoluteFill className="v2-scene-root">
        <div className="v2-resume-copy" style={{opacity: fadeInOut(frame, 0, 330, 22), translate: `0px ${(1 - p(frame, 0, 28)) * 22}px`}}>
          <MicroLabel color="#8494aa" start={2}>THE NEXT DAY / RESUME</MicroLabel>
          <h2>Come back<br /><span>to the search.</span></h2>
          <p>The camera does not return to the beginning.<br />It resumes at the unfinished node.</p>
        </div>
        <div className="v2-resume-darkness" style={{opacity: darkness * (1 - p(frame, 250, 330))}} />
        <div className="v2-resume-line" style={{scale: `${p(frame, 0, 86)} 1`, opacity: .65}} />
        <Terminal
          className="v2-resume-terminal"
          title="~/research-project"
          tag="RESUME"
          start={46}
          lines={[
            {text: '$ ./scripts/research-agent resume', tone: 'blue', delay: 22},
            {text: '  --cli codex --target ./project', tone: 'muted', delay: 48},
            {text: '  › restoring State S004', tone: 'violet', delay: 89},
            {text: '  › next action / ready', tone: 'green', delay: 126},
          ]}
          style={{opacity: restore, scale: camera(frame, [0, 68, 300], [.985, 1, 1.01]), translate: `${camera(frame, [0, 68, 300], [34, 0, 0])}px 0px`}}
        />
        <V2World className="v2-resume-world" size={208} start={145} color={V2C.green} label="STATE S004" detail="resume from evidence" style={{opacity: world}} />
        <FileToken className="v2-resume-file-1" name="STATE.yaml" sub="restored" color={V2C.green} start={171} />
        <FileToken className="v2-resume-file-2" name="next-action" sub="ready" color={V2C.cyan} start={204} />
        <svg className="v2-resume-trace" viewBox="0 0 1920 1080" preserveAspectRatio="none"><Trace d="M765 734 C999 734 1085 672 1267 623 C1443 577 1560 490 1777 420" color={V2C.green} start={152} duration={128} width={2} opacity={world} /></svg>
        <div className="v2-resume-bottom" style={{opacity: p(frame, 236, 278)}}><Dot color={V2C.green} size={7} glow /> <span>THE SEARCH IS STILL HERE.</span></div>
      </AbsoluteFill>
    </Surface>
  );
};
