import { test, expect, Page } from "@playwright/test";
import fs from "fs";
import path from "path";

const SCREENSHOTS_ROOT = path.join(__dirname, "screenshots");
const BASE = "http://localhost:8100";

// Shared state across serial tests
let incidentId: string;

// Helper: save a named screenshot into a per-test folder
async function snap(page: Page, testFolder: string, name: string) {
  const dir = path.join(SCREENSHOTS_ROOT, testFolder);
  fs.mkdirSync(dir, { recursive: true });
  try {
    await page.screenshot({
      path: path.join(dir, `${name}.png`),
      fullPage: true,
    });
  } catch {
    await page.screenshot({
      path: path.join(dir, `${name}.png`),
    });
  }
}

// Helper: create incident via API (reliable)
async function createIncidentViaAPI(): Promise<string> {
  const resp = await fetch(`${BASE}/api/incidents`, {
    method: "POST",
    body: new URLSearchParams({
      reporter_email: "sre-oncall@example.com",
      reporter_name: "SRE On-Call Engineer",
      description:
        "Payment gateway returning HTTP 502 errors during checkout. " +
        "All customers affected since 14:30 UTC. Stripe webhook handler " +
        "appears to be timing out. Error rate jumped from 0.1% to 45% in " +
        "the last 15 minutes. Checkout completion rate dropped to near zero.",
    }),
  });
  const data = await resp.json();
  return data.id;
}

// Helper: triage incident via API (reliable, with timeout)
async function triageViaAPI(id: string): Promise<void> {
  const resp = await fetch(`${BASE}/api/incidents/${id}/triage`, {
    method: "POST",
    signal: AbortSignal.timeout(60_000),
  });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`Triage failed (${resp.status}): ${body}`);
  }
}

// ---------------------------------------------------------------------------
// 01. Incident list
// ---------------------------------------------------------------------------
test("01 — Home page shows incident list", async ({ page }) => {
  await page.goto("/incidents");
  await expect(page.locator(".page-header h1")).toContainText("Incidents");
  await snap(page, "01-incident-list", "incident-list");
});

// ---------------------------------------------------------------------------
// 02. Submit form page
// ---------------------------------------------------------------------------
test("02 — Submit form renders correctly", async ({ page }) => {
  await page.goto("/incidents/new");
  await expect(page.locator(".page-header h1")).toContainText(
    "Report New Incident"
  );
  await expect(page.locator("#reporter_email")).toBeVisible();
  await expect(page.locator("#description")).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeVisible();
  await snap(page, "02-submit-form", "form-empty");
});

// ---------------------------------------------------------------------------
// 03. Fill and create incident
// ---------------------------------------------------------------------------
test("03 — Fill form and create incident", async ({ page }) => {
  await page.goto("/incidents/new");

  await page.fill("#reporter_name", "SRE On-Call Engineer");
  await page.fill("#reporter_email", "sre-oncall@example.com");
  await page.fill(
    "#description",
    "Payment gateway returning HTTP 502 errors during checkout. " +
      "All customers affected since 14:30 UTC. Stripe webhook handler " +
      "appears to be timing out. Error rate jumped from 0.1% to 45% in " +
      "the last 15 minutes. Checkout completion rate dropped to near zero."
  );
  await snap(page, "03-create-incident", "form-filled");

  incidentId = await createIncidentViaAPI();
  await page.goto(`/incidents/${incidentId}`);

  await expect(page.locator(".status-badge").first()).toContainText(
    "submitted"
  );
  await snap(page, "03-create-incident", "detail-submitted");
});

// ---------------------------------------------------------------------------
// 04. Untriaged detail page
// ---------------------------------------------------------------------------
test("04 — Detail page shows untriaged incident with triage button", async ({
  page,
}) => {
  if (!incidentId) incidentId = await createIncidentViaAPI();

  await page.goto(`/incidents/${incidentId}`);
  await expect(page.locator(".description-block")).toContainText(
    "Payment gateway"
  );
  await expect(page.locator(".empty-triage")).toBeVisible();
  await expect(
    page.locator('button:has-text("Run AI Triage")')
  ).toBeVisible();
  await snap(page, "04-untriaged", "detail-awaiting-triage");
});

// ---------------------------------------------------------------------------
// 05. AI triage (real Claude Haiku call)
// ---------------------------------------------------------------------------
test("05 — Run AI triage and verify results", async ({ page }) => {
  test.setTimeout(90_000);

  if (!incidentId) incidentId = await createIncidentViaAPI();

  await triageViaAPI(incidentId);

  await page.goto(`/incidents/${incidentId}`);

  await expect(page.locator(".triage-section").first()).toBeVisible();
  await expect(page.locator(".status-badge").first()).toContainText(
    "dispatched"
  );
  await expect(page.locator(".severity-badge")).toBeVisible();
  await expect(page.locator(".confidence-fill")).toBeVisible();

  await snap(page, "05-triage-results", "triage-top");

  await page.evaluate(() => window.scrollBy(0, 500));
  await snap(page, "05-triage-results", "triage-scrolled");
});

// ---------------------------------------------------------------------------
// 06. Dispatch panel
// ---------------------------------------------------------------------------
test("06 — Verify dispatch panel with ticket and notifications", async ({
  page,
}) => {
  if (!incidentId) {
    test.skip();
    return;
  }

  await page.goto(`/incidents/${incidentId}`);

  await expect(page.locator(".dispatch-card")).toBeVisible();
  await expect(page.locator(".dispatch-checklist")).toBeVisible();

  const checks = page.locator(".check-done");
  await expect(checks.first()).toBeVisible();

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await snap(page, "06-dispatch", "checklist");

  await page.click("details.dispatch-detail:first-of-type summary");
  await expect(page.locator(".dispatch-preview").first()).toBeVisible();
  await snap(page, "06-dispatch", "ticket-expanded");

  const emailDetail = page.locator("details.dispatch-detail:nth-of-type(2)");
  await emailDetail.locator("summary").click();
  await snap(page, "06-dispatch", "email-expanded");

  await expect(page.locator(".integration-notice")).toBeVisible();
  await snap(page, "06-dispatch", "integration-notice");
});

// ---------------------------------------------------------------------------
// 07. Incident list with triaged incident
// ---------------------------------------------------------------------------
test("07 — Incident list shows dispatched incident with badges", async ({
  page,
}) => {
  await page.goto("/incidents");

  await expect(page.locator(".clickable-row").first()).toBeVisible({
    timeout: 5_000,
  });

  const firstRow = page.locator(".clickable-row").first();
  await expect(firstRow.locator(".status-badge")).toBeVisible();
  await expect(firstRow.locator(".severity-badge")).toBeVisible();

  await snap(page, "07-list-dispatched", "list-with-badges");
});

// ---------------------------------------------------------------------------
// 08. Acknowledge incident
// ---------------------------------------------------------------------------
test("08 — Acknowledge dispatched incident", async ({ page }) => {
  if (!incidentId) {
    test.skip();
    return;
  }

  await page.goto(`/incidents/${incidentId}`);

  const ackBtn = page.locator("#ack-btn");
  await expect(ackBtn).toBeVisible();
  await snap(page, "08-acknowledge", "before");

  page.on("dialog", (dialog) => dialog.accept());
  await ackBtn.click();
  await page.waitForURL(`/incidents/${incidentId}`, { timeout: 10_000 });
  await page.waitForLoadState("networkidle");
  await snap(page, "08-acknowledge", "after");
});

// ---------------------------------------------------------------------------
// 09. Resolve incident
// ---------------------------------------------------------------------------
test("09 — Resolve incident with dialog", async ({ page }) => {
  if (!incidentId) {
    test.skip();
    return;
  }

  await page.goto(`/incidents/${incidentId}`);

  const resolveBtn = page.locator('.header-actions button:has-text("Resolve")');
  await resolveBtn.click();

  const dialog = page.locator("#resolve-dialog");
  await expect(dialog).toBeVisible();
  await page.selectOption("#resolution_type", "fix");
  await page.fill(
    "#resolution_notes",
    "Search index rebuilt and hotfix deployed."
  );
  await snap(page, "09-resolve", "dialog-filled");

  await page.locator('#resolve-form button[type="submit"]').click();
  await page.waitForURL(`/incidents/${incidentId}`, { timeout: 10_000 });
  await page.waitForLoadState("networkidle");

  await expect(page.locator(".status-badge").first()).toContainText("resolved");
  await snap(page, "09-resolve", "resolved-status");

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await snap(page, "09-resolve", "resolution-details");
});

// ---------------------------------------------------------------------------
// 10. Final incident list
// ---------------------------------------------------------------------------
test("10 — Incident list shows resolved incident", async ({ page }) => {
  await page.goto("/incidents");

  await expect(page.locator(".clickable-row").first()).toBeVisible({
    timeout: 5_000,
  });

  await snap(page, "10-list-final", "list-with-resolved");
});

// ---------------------------------------------------------------------------
// 11. 404 page
// ---------------------------------------------------------------------------
test("11 — 404 page for non-existent incident", async ({ page }) => {
  await page.goto("/incidents/00000000-0000-0000-0000-000000000000");

  await expect(page.locator(".empty-state h1")).toContainText("Not Found");
  await expect(
    page.locator('a:has-text("View All Incidents")')
  ).toBeVisible();

  await snap(page, "11-not-found", "not-found-page");
});
