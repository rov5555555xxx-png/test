const { chromium } = require('playwright');
const { spawn } = require('child_process');
(async () => {
  const [page_, mode, out, fpsArg] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + page_); await p.evaluate(() => window.ready);
  if (mode === 'stills') {
    for (const t of out.split(',')) { await p.evaluate(t => renderAt(t), +t); await p.screenshot({ path: `${fpsArg}/still_${t}.jpg`, type: 'jpeg', quality: 80 }); }
  } else {
    const fps = +fpsArg, dur = +mode, n = Math.ceil(dur * fps);
    const ff = spawn('ffmpeg', ['-v','error','-y','-f','image2pipe','-framerate',String(fps),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium',out], { stdio: ['pipe','inherit','inherit'] });
    for (let i = 0; i < n; i++) { await p.evaluate(t => renderAt(t), i / fps); const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); if (i % 60 === 0) console.log('frame', i, '/', n); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close();
})();
