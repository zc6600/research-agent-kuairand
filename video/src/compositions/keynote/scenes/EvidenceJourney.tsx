import React from 'react';
import {Img, staticFile} from 'remotion';
import {progress, travel} from '../motion';

export function EvidenceJourney({frame}: {frame: number}) {
  const scroll = progress(frame, 1200, 1258);
  const focus = progress(frame, 1280, 1340);
  return <div className="kn-dashboard" style={{opacity: progress(frame, 1080, 1115) * (1 - progress(frame, 1390, 1434))}}>
    <div className="kn-dashboard-viewport">
      <div style={{position: 'absolute', inset: 0, translate: `0 ${-760 * scroll}px`, opacity: 1 - scroll}}>
        <Img src={staticFile('assets/dashboard-overview.png')} style={{width: '100%', display: 'block'}} />
      </div>
      <div style={{position: 'absolute', inset: 0, translate: `0 ${(1 - scroll) * 760}px`, opacity: scroll * (1 - focus * 0.65)}}>
        <Img src={staticFile('assets/dashboard-validation.png')} style={{width: '100%', display: 'block'}} />
      </div>
      <div style={{position: 'absolute', left: travel(frame, [1280, 1340], [822, 335]), top: travel(frame, [1280, 1340], [286, 220]), width: 480, height: 150, overflow: 'hidden', opacity: focus, scale: travel(frame, [1280, 1340], [0.57, 2.2]), transformOrigin: '0 0'}}>
        {/* Exact displayed value, re-typeset for a sharp close-up after the real UI reveal. */}
        <div style={{position: 'absolute', inset: 0, background: '#fff', border: '1px solid #e6e9ed', boxShadow: '0 18px 46px rgba(22,34,48,.13)', fontFamily: 'Arial, sans-serif'}}>
          <div style={{position: 'absolute', left: 52, top: 18, fontSize: 24, fontWeight: 600, color: '#333f52'}}>Primary</div>
          <div style={{position: 'absolute', left: 52, top: 58, fontSize: 44, fontWeight: 600, color: '#609f7c'}}>0.605936</div>
          <div style={{position: 'absolute', left: 0, right: 0, bottom: 10, height: 1, background: '#eceef1'}} />
        </div>
      </div>
      <div style={{position: 'absolute', left: 445, top: 150, opacity: focus, color: '#737b84', fontSize: 25}}>Retained checkpoint · S004</div>
    </div>
    <div className="kn-recorded">Recorded KuaiRand example · public validation</div>
  </div>;
}
