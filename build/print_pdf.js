// Prints a standalone HTML file to PDF with page numbers using headless Chromium.
// Usage: node print_pdf.js <input.html> <output.pdf> "<running title>"
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [input, output, title] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(input), { waitUntil: 'load', timeout: 0 });
  await page.emulateMedia({ media: 'print', colorScheme: 'light' });
  await page.evaluate(() => {
    document.documentElement.setAttribute('data-theme', 'light');
    document.querySelectorAll('details').forEach((d) => { d.open = true; });
  });
  const esc = (s) => String(s || '').replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  await page.pdf({
    path: output,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: `<div style="font-family:Inter,sans-serif;font-size:7.5px;color:#8A94A6;width:100%;padding:0 20mm;text-align:right;">${esc(title)}</div>`,
    footerTemplate: '<div style="font-family:Inter,sans-serif;font-size:8px;color:#57606A;width:100%;text-align:center;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    margin: { top: '22mm', bottom: '22mm', left: '20mm', right: '20mm' },
    timeout: 0,
  });
  await browser.close();
})();
