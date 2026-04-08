import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false, // sequential — tests build on each other
  retries: 0,
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: "http://localhost:8100",
    screenshot: "on",
    trace: "retain-on-failure",
    viewport: { width: 1280, height: 800 },
  },
  outputDir: "./e2e/test-results",
  projects: [
    {
      name: "chromium",
      use: { browserName: "chromium" },
    },
  ],
});
