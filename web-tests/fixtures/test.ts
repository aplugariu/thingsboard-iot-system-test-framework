import { randomUUID } from 'node:crypto';
import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/login-page';
import { DevicesPage } from '../pages/devices-page';

type Credentials = {
  username: string;
  password: string;
};

type Device = {
  id: string;
  name: string;
};

type Fixtures = {
  credentials: Credentials;
  device: Device;
  loginPage: LoginPage;
  devicesPage: DevicesPage;
};

export const test = base.extend<Fixtures>({
  credentials: async ({}, use) => {
    const username = process.env.TB_TENANT_USERNAME;
    const password = process.env.TB_TENANT_PASSWORD;

    if (!username || !password) {
      throw new Error('Set TB_TENANT_USERNAME and TB_TENANT_PASSWORD.');
    }

    await use({ username, password });
  },

  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  devicesPage: async ({ page }, use) => {
    await use(new DevicesPage(page));
  },

  device: async ({ request, credentials }, use) => {
    const login = await request.post('/api/auth/login', {
      data: credentials,
    });
    expect(login.status(), 'API tenant login should succeed').toBe(200);

    const auth = await login.json();
    if (typeof auth.token !== 'string' || !auth.token) {
      throw new Error('API login did not return a token.');
    }

    const headers = {
      'X-Authorization': `Bearer ${auth.token}`,
    };
    const name = `test-ui-device-${randomUUID()}`;

    const created = await request.post('/api/device', {
      headers,
      data: { name, type: 'default' },
    });
    expect(created.status(), 'Device creation should succeed').toBe(200);

    const body = await created.json();
    const id: string = body.id.id;

    try {
      await use({ id, name });
    } finally {
      const deleted = await request.delete(`/api/device/${id}`, {
        headers,
      });
      expect(
        deleted.status(),
        `Cleanup should delete device ${id}`,
      ).toBe(200);
    }
  },
});
