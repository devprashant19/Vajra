const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const contextDesktop = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2
  });
  
  const page = await contextDesktop.newPage();
  const outDir = path.join(__dirname, '../../docs/ui/screenshots');

  console.log('Capturing Landing Page...');
  await page.goto('http://localhost:8080/', { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(outDir, '01-landing.png') });

  console.log('Capturing Map Timeline...');
  await page.goto('http://localhost:8080/map.html', { waitUntil: 'networkidle' });
  // wait for map to load frames
  await page.waitForTimeout(5000);
  await page.screenshot({ path: path.join(outDir, '02-map-timeline.png') });

  console.log('Capturing Scenario Picker...');
  // Click scenario dropdown
  const scenarioBtn = page.locator('text=SIMULATED').first();
  if (await scenarioBtn.isVisible()) {
      await scenarioBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(outDir, '08-scenario-picker.png') });
      await page.keyboard.press('Escape'); // close it
  }

  console.log('Capturing Cell Inspector...');
  // click middle of the map
  await page.mouse.click(720, 450);
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(outDir, '04-cell-inspector.png') });

  console.log('Capturing Alert Composer...');
  const draftBtn = page.locator('text=Draft Alert');
  if (await draftBtn.isVisible()) {
      await draftBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: path.join(outDir, '05-alert-composer.png') });
      await page.keyboard.press('Escape');
  }

  console.log('Capturing Countdown Rail...');
  // Just capture the map again or specific area if rail exists
  await page.screenshot({ path: path.join(outDir, '03-countdown-rail.png') });

  console.log('Capturing Real Data Page...');
  await page.goto('http://localhost:8080/data.html', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(outDir, '06-real-data.png') });

  await contextDesktop.close();

  console.log('Capturing Mobile...');
  const contextMobile = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
    isMobile: true
  });
  const mPage = await contextMobile.newPage();
  await mPage.goto('http://localhost:8080/m.html', { waitUntil: 'networkidle' });
  await mPage.waitForTimeout(2000);
  await mPage.screenshot({ path: path.join(outDir, '07-mobile-public.png') });
  await contextMobile.close();

  await browser.close();
  console.log('Done!');
})();
