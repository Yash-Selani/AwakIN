import { test, expect } from '@playwright/test';

test('user flow: login -> disasters -> map', async ({ page }) => {
  await page.goto('/');

  // Assuming it redirects to /login if not logged in
  await expect(page).toHaveURL(/.*login/);
  
  // Fill login
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Should redirect to dashboard
  await expect(page).toHaveURL(/.*\/$/);
  await expect(page.locator('text=Welcome to AwakIN')).toBeVisible();

  // Navigate to Disasters
  await page.click('text=Emergency Guidelines');
  await expect(page).toHaveURL(/.*disasters/);

  // Click on Flood
  await page.click('text=Flood');
  await expect(page.locator('text=AI Situation Guide')).toBeVisible();

  // Navigate to Map
  await page.click('text=Map');
  await expect(page).toHaveURL(/.*map/);
  await expect(page.locator('.gm-style')).toBeVisible({ timeout: 10000 }); // Google Maps canvas
});
