const {chromium} = require('/Users/kevin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
  const directory = process.argv[2];
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 736, height: 850}});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto('file://' + path.join(directory, 'viewer-preview.html'));
    const view = page.frames().find(f => f.parentFrame());
    if (!view) throw Error('Missing visualization iframe');
    const image = view.locator('[data-image]');
    await image.evaluate(i => i.decode());
    const first = await image.getAttribute('src');
    await view.getByRole('button', {name: 'Play recorded steps'}).click();
    await page.waitForTimeout(450);
    if (await view.locator('[data-frame]').inputValue() === '0') throw Error('Playback did not advance');
    await view.getByRole('button', {name: 'Pause'}).click();
    const paused = await view.locator('[data-frame]').inputValue();
    await page.waitForTimeout(300);
    if (await view.locator('[data-frame]').inputValue() !== paused) throw Error('Pause did not stop');
    await view.locator('[data-frame]').focus();
    await view.locator('[data-frame]').press('End');
    if (await view.locator('[data-frame]').inputValue() !== '16') throw Error('Frame slider End failed');
    if (await image.getAttribute('src') === first) throw Error('Final frame remained unchanged');
    await view.getByRole('combobox', {name: 'Choose actor'}).selectOption('1');
    await image.evaluate(i => i.decode());
    if (!(await image.getAttribute('alt')).includes('actor B')) throw Error('Actor selection failed');
    const sizes = [];
    for (const width of [736, 320]) {
      await page.setViewportSize({width, height: 850});
      await page.waitForTimeout(100);
      const size = await view.evaluate(() => ({width: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth, imageWidth: document.querySelector('[data-image]').clientWidth, loaded: document.querySelector('[data-image]').naturalWidth}));
      if (size.scroll > size.width + 1 || size.loaded !== 672) throw Error(JSON.stringify(size));
      sizes.push(size);
      await page.screenshot({path: path.join(directory, 'viewer-' + width + '.png'), fullPage: true});
    }
    if (errors.length) throw Error(errors.join('\n'));
    fs.writeFileSync(path.join(directory, 'viewer-QA.json'), JSON.stringify({status:'headless_browser_play_pause_scrub_actor_selection_and_responsive_layout_pass',sizes,native_LM_Studio_Chat_verified:false},null,2)+'\n');
    console.log('Viewer interactions and responsive layout passed');
  } finally { await browser.close(); }
})().catch(e => {console.error(e); process.exitCode = 1;});
