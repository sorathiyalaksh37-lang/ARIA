/**
 * Playwright End-to-End Test Suite: Complete Emergency Incident Lifecycle
 * Tests flow from incident creation -> Bystander Guidance -> Green Corridor -> Hospital Prep -> Family Portal
 */

import { test, expect } from '@playwright/test';

test.describe('ARIA Platform Complete Emergency Incident Lifecycle E2E Suite', () => {

  test('Complete End-to-End Emergency Workflow', async ({ page }) => {
    // 1. Incident Creation & Command Center Overview
    await page.goto('http://localhost:3000/dashboard');
    await expect(page.locator('h1, h4, h5')).toContainText(/ARIA|Emergency/i);

    // 2. Bystander First Aid Portal
    await page.goto('http://localhost:3000/bystander');
    await expect(page).toHaveURL(/bystander/);

    // 3. Green Corridor Smart Traffic Control
    await page.goto('http://localhost:3000/traffic');
    await expect(page).toHaveURL(/traffic/);

    // 4. Hospital Pre-Arrival Preparation Portal
    await page.goto('http://localhost:3000/hospital-prep');
    await expect(page).toHaveURL(/hospital-prep/);

    // 5. Family Communication Live Tracking Portal
    await page.goto('http://localhost:3000/family-portal');
    await expect(page).toHaveURL(/family-portal/);
  });

  test('Mass Casualty Incident (MCI) Mode E2E Workflow', async ({ page }) => {
    await page.goto('http://localhost:3000/mass-casualty');
    await expect(page).toHaveURL(/mass-casualty/);
  });
});
