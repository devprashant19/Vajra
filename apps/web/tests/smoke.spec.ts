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
  await expect(page.locator('text=Administrative boundaries not shown')).toBeVisible();
  const content = await page.content();
  expect(content).not.toContain('cartocdn.com');
  expect(content).not.toContain('openstreetmap.org');
});
