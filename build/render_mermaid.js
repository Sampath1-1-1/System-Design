// Renders Mermaid diagrams to SVG and PNG with headless Chromium.
// Usage: node render_mermaid.js <jobs.json>
// jobs.json: [{"id": "fig-07-03-<hash>", "code": "...", "out": "/abs/dir"}]
// Prints a JSON array of {id, ok, error} to stdout.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const MERMAID = path.join(__dirname, 'node_modules', 'mermaid', 'dist', 'mermaid.min.js');

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2, viewport: { width: 1400, height: 1000 } });
  await page.setContent('<!doctype html><html><body style="margin:0;background:#fff"><div id="host"></div></body></html>');
  await page.addScriptTag({ path: MERMAID });
  await page.evaluate(() => {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'loose',
      theme: 'base',
      fontFamily: 'Inter, DejaVu Sans, sans-serif',
      flowchart: { htmlLabels: false, curve: 'basis', useMaxWidth: false },
      sequence: { useMaxWidth: false, mirrorActors: false },
      themeVariables: {
        primaryColor: '#EEF4FB', primaryBorderColor: '#1F5FA8', primaryTextColor: '#1B2A4A',
        lineColor: '#4A5568', secondaryColor: '#ECF6F6', tertiaryColor: '#F4F5F7',
        clusterBkg: '#F7F9FC', clusterBorder: '#A0AEC0', fontSize: '15px',
        actorBkg: '#EEF4FB', actorBorder: '#1F5FA8', noteBkgColor: '#FBF4E6', noteBorderColor: '#B7791F',
      },
    });
  });
  const results = [];
  for (const job of jobs) {
    try {
      const svg = await page.evaluate(async ({ id, code }) => {
        const { svg } = await mermaid.render('d' + id.replace(/[^a-zA-Z0-9]/g, '_'), code);
        return svg;
      }, job);
      fs.mkdirSync(job.out, { recursive: true });
      fs.writeFileSync(path.join(job.out, job.id + '.svg'), svg);
      await page.evaluate((svg) => { document.getElementById('host').innerHTML = svg; }, svg);
      const el = await page.$('#host svg');
      await el.screenshot({ path: path.join(job.out, job.id + '.png'), omitBackground: false });
      results.push({ id: job.id, ok: true });
    } catch (e) {
      results.push({ id: job.id, ok: false, error: String(e && e.message || e).slice(0, 300) });
    }
  }
  await browser.close();
  process.stdout.write(JSON.stringify(results));
})();
