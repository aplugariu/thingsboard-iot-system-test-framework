import { test } from '../fixtures/test';

test('API-created device appears in the UI', async ({
  device,
  credentials,
  loginPage,
  devicesPage,
}) => {
  await loginPage.login(credentials.username, credentials.password);
  await devicesPage.open();
  await devicesPage.search(device.name);
  await devicesPage.expectDeviceVisible(device.name);
});
