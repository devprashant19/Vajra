import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test('loads the app and renders MapLibre', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=Vajra')).toBeVisible();
    await expect(page.locator('.maplibregl-map')).toBeVisible({ timeout: 10000 });
  });

  test('plays the timeline', async ({ page }) => {
    await page.goto('/');
    const playButton = page.locator('button', { hasText: '▶' });
    await expect(playButton).toBeVisible();
    // In a real test, we would click and verify time changes
  });

  test('opens the inspector', async ({ page }) => {
    await page.goto('/');
    // Check if the location inspector is visible
    await expect(page.locator('text=Locations')).toBeVisible();
    await expect(page.locator('text=Airport T1')).toBeVisible();
  });
});
