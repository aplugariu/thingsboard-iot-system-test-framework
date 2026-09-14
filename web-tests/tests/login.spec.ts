import { test, expect } from '@playwright/test';

test('tenant administrator can sign in through the UI', async ({ page }) => {
  const username = process.env.TB_TENANT_USERNAME;
  const password = process.env.TB_TENANT_PASSWORD;

  if (!username || !password) {
    throw new Error('Set TB_TENANT_USERNAME and TB_TENANT_PASSWORD.');
  }

  await page.goto('/login');

  await page.getByRole('textbox', {
    name: 'Username (email)',
    exact: true,
  }).fill(username);

  await page.getByRole('textbox', {
    name: 'Password',
    exact: true,
  }).fill(password);

  const loginResponsePromise = page.waitForResponse(
    response =>
      new URL(response.url()).pathname === '/api/auth/login' &&
      response.request().method() === 'POST',
  );

  await page.getByRole('button', {
    name: 'Sign in',
    exact: true,
  }).click();

  const loginResponse = await loginResponsePromise;
  expect(loginResponse.status(), 'UI login should succeed').toBe(200);

  await expect(page).not.toHaveURL(/\/login(?:[/?#]|$)/);
  await expect(
    page.getByRole('button', { name: 'Sign in', exact: true }),
  ).not.toBeVisible();
});
