import { expect, type Page } from '@playwright/test';

export class DevicesPage {
  constructor(private page: Page) {}

    async open() {
    await this.page.goto('/entities/devices');

    await expect(this.page).toHaveURL(/\/entities\/devices(?:[/?#]|$)/);
    await expect(this.page.getByRole('table')).toBeVisible();
  }

  async search(name: string) {
    const searchInput = this.page.getByPlaceholder('Search devices');

    if (!(await searchInput.isVisible())) {
      await this.page.getByRole('button', {
        description: 'Search devices',
        exact: true,
      }).click();
    }

    await expect(searchInput).toBeVisible();
    await searchInput.fill(name);
  }

  async expectDeviceVisible(name: string) {
    await expect(
      this.page.getByRole('table').getByText(name, { exact: true }),
    ).toBeVisible();
  }
}
