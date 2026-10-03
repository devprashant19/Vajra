import { test, expect } from '@playwright/test';

test('Honesty labels are present on the landing page', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('text=SIMULATED DATA ONLY')).toBeVisible();
});

test('Honesty labels are present on the map page', async ({ page }) => {
  await page.goto('/map');
  await expect(page.locator('text=SIMULATED DATA - NOT EVIDENCE')).toBeVisible();
  await expect(page.locator('text=SKILFUL: UNKNOWN')).toBeVisible();
});

test('Mobile page has simulated notice and reliability warning', async ({ page }) => {
  await page.goto('/m');
  await expect(page.locator('text=SIMULATED DATA - NOT EVIDENCE')).toBeVisible();
  await expect(page.locator('text=SKILFUL: UNKNOWN')).toBeVisible();
});

test('MapLibre basemap does not have administrative boundaries', async ({ page }) => {
  await page.goto('/map');
  // Check the source URL for the basemap to ensure it uses the 'nolabels' or clean tile source
  // The UI currently uses https://a.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}@2x.png
  const content = await page.content();
  expect(content).toContain('dark_nolabels');
});
