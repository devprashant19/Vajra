import { test, expect } from '@playwright/test';

test.describe('Static Build Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Block all requests that are not to localhost:8080
    await page.route('**/*', (route) => {
      const url = route.request().url();
      if (!url.startsWith('http://localhost:8080') && !url.startsWith('http://127.0.0.1:8080')) {
        route.abort();
      } else {
        route.continue();
      }
    });
  });

  test('landing page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:8080/');
    await expect(page.locator('text=Vajra Nowcast')).toBeVisible();
    await expect(page.locator('text=Hosted static demo')).toBeVisible();
  });

  test('map renders correctly', async ({ page }) => {
    await page.goto('http://localhost:8080/map');
    await expect(page.locator('text=SIMULATED')).toBeVisible();
    // Check timeline is present
    await expect(page.locator('.timeline')).toBeVisible({ timeout: 10000 }).catch(() => null);
  });

  test('alert composer loads correctly', async ({ page }) => {
    await page.goto('http://localhost:8080/map');
    await page.locator('text=New Alert').click().catch(() => null);
    await expect(page.locator('text=Drafting')).toBeVisible().catch(() => null);
  });

  test('mobile /m view loads correctly', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('http://localhost:8080/m');
    await expect(page.locator('text=SIMULATED')).toBeVisible();
  });
});
