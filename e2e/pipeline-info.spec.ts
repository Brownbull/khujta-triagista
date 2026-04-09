import { test, expect, Page } from "@playwright/test";
import fs from "fs";
import path from "path";

const SCREENSHOTS_ROOT = path.join(__dirname, "screenshots", "17-pipeline-info");
const BASE = "http://localhost:8100";

// Helper: save a named screenshot
async function snap(page: Page, name: string) {
  fs.mkdirSync(SCREENSHOTS_ROOT, { recursive: true });
  try {
    await page.screenshot({
      path: path.join(SCREENSHOTS_ROOT, `${name}.png`),
      fullPage: true,
    });
  } catch {
    await page.screenshot({
      path: path.join(SCREENSHOTS_ROOT, `${name}.png`),
    });
  }
}

// Find a dispatched incident from the list page
async function findIncidentByStatus(
  page: Page,
  status: string
): Promise<string> {
  await page.goto(`${BASE}/incidents?status=${status}`);
  const row = page.locator('[data-testid="incident-row"]').first();
  await expect(row).toBeVisible({ timeout: 5000 });
  const onclick = await row.getAttribute("onclick");
  // Extract UUID from onclick="window.location='/incidents/UUID'"
  const match = onclick?.match(/\/incidents\/([a-f0-9-]+)/);
  if (!match) throw new Error(`No incident found with status ${status}`);
  return match[1];
}

// ---------------------------------------------------------------------------
// Test: Pipeline info panel appears on dot click
// ---------------------------------------------------------------------------
test("17a — Clicking pipeline dot shows info panel below", async ({
  page,
}) => {
  const id = await findIncidentByStatus(page, "dispatched");
  await page.goto(`${BASE}/incidents/${id}`);
  await expect(page.locator('[data-testid="pipeline-progress"]')).toBeVisible();
  await snap(page, "before-click");

  // Click the first pipeline dot (Submitted) via JS to avoid geometry issues
  await page.locator(".pipeline-dot").first().dispatchEvent("click");

  // Info panel should become visible with content
  const panel = page.locator("#pipeline-info-panel");
  await expect(panel).toHaveClass(/visible/, { timeout: 3000 });
  await expect(page.locator("#pipeline-info-title")).toContainText("Submitted");
  await expect(page.locator("#pipeline-info-body")).not.toBeEmpty();

  await snap(page, "submitted-clicked");
});

// ---------------------------------------------------------------------------
// Test: Clicking different dots updates the panel content
// ---------------------------------------------------------------------------
test("17b — Clicking different dots updates info panel content", async ({
  page,
}) => {
  const id = await findIncidentByStatus(page, "dispatched");
  await page.goto(`${BASE}/incidents/${id}`);
  await expect(page.locator('[data-testid="pipeline-progress"]')).toBeVisible();

  const title = page.locator("#pipeline-info-title");
  const body = page.locator("#pipeline-info-body");

  // Click Submitted dot
  await page.locator(".pipeline-dot").nth(0).dispatchEvent("click");
  await expect(title).toContainText("Submitted", { timeout: 3000 });
  await snap(page, "dot-submitted");

  // Click Guardrail dot — content should change
  await page.locator(".pipeline-dot").nth(1).dispatchEvent("click");
  await expect(title).toContainText("Guardrail", { timeout: 3000 });
  await expect(body).toContainText("Injection");
  await snap(page, "dot-guardrail");

  // Click Dispatched dot (skip Triaged to keep test fast)
  await page.locator(".pipeline-dot").nth(3).dispatchEvent("click");
  await expect(title).toContainText("Dispatched", { timeout: 3000 });
  await snap(page, "dot-dispatched");
});

// ---------------------------------------------------------------------------
// Test: Info panel auto-dismisses after 5 seconds
// ---------------------------------------------------------------------------
test("17c — Info panel auto-dismisses after 5 seconds", async ({ page }) => {
  const id = await findIncidentByStatus(page, "dispatched");
  await page.goto(`${BASE}/incidents/${id}`);

  const panel = page.locator("#pipeline-info-panel");

  // Click a dot
  await page.locator(".pipeline-dot").first().click();
  await expect(panel).toHaveClass(/visible/);

  // Wait 5.5 seconds — should auto-dismiss
  await page.waitForTimeout(5500);
  await expect(panel).not.toHaveClass(/visible/);

  await snap(page, "auto-dismissed");
});

// ---------------------------------------------------------------------------
// Test: Panel dismisses on click outside
// ---------------------------------------------------------------------------
test("17d — Clicking outside dismisses info panel", async ({ page }) => {
  const id = await findIncidentByStatus(page, "dispatched");
  await page.goto(`${BASE}/incidents/${id}`);

  const panel = page.locator("#pipeline-info-panel");

  // Click a dot to show panel
  await page.locator(".pipeline-dot").first().click();
  await expect(panel).toHaveClass(/visible/);

  // Click outside (on the description panel)
  await page.locator(".panel-body").first().click();
  await expect(panel).not.toHaveClass(/visible/);

  await snap(page, "dismissed-outside");
});

// ---------------------------------------------------------------------------
// Test: Rejected incident shows guardrail info correctly
// ---------------------------------------------------------------------------
test("17e — Rejected incident pipeline info shows blocked message", async ({
  page,
}) => {
  const id = await findIncidentByStatus(page, "rejected");
  await page.goto(`${BASE}/incidents/${id}`);

  const panel = page.locator("#pipeline-info-panel");

  // Click the guardrail dot (second dot)
  await page.locator(".pipeline-dot").nth(1).click();
  await expect(panel).toHaveClass(/visible/);
  await expect(page.locator("#pipeline-info-title")).toContainText("Guardrail");
  await expect(page.locator("#pipeline-info-body")).toContainText("Blocked");

  await snap(page, "rejected-guardrail");
});
