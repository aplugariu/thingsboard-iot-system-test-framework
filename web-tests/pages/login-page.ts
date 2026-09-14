import { expect, type Page } from '@playwright/test';

export class LoginPage {
  constructor(private page: Page) {}

  async login(username: string, password: string) {
    await this.page.goto('/login');

    await this.page.getByRole('textbox', {
      name: 'Username (email)',
      exact: true,
    }).fill(username);

    await this.page.getByRole('textbox', {
      name: 'Password',
      exact: true,
    }).fill(password);

    const responsePromise = this.page.waitForResponse(
      response =>
        new URL(response.url()).pathname === '/api/auth/login' &&
        response.request().method() === 'POST',
    );

    await this.page.getByRole('button', {
      name: 'Sign in',
      exact: true,
    }).click();

    const response = await responsePromise;
    expect(response.status(), 'UI login should succeed').toBe(200);
    await expect(this.page).not.toHaveURL(/\/login(?:[/?#]|$)/);
  }
}
