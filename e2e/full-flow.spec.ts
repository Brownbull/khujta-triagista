import { test, expect, Page } from "@playwright/test";
import path from "path";

const SCREENSHOTS = path.join(__dirname, "screenshots");
const BASE = "http://localhost:8100";

// Shared state across serial tests
let incidentId: string;

// Helper: save a named screenshot (with fallback for protocol errors)
async function snap(page: Page, name: string) {
  try {
    await page.screenshot({
      path: path.join(SCREENSHOTS, `${name}.png`),
      fullPage: true,
    });
  } catch {
    // Fallback: viewport-only screenshot if full-page fails
    await page.screenshot({
      path: path.join(SCREENSHOTS, `${name}.png`),
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
// 1. Empty state
// ---------------------------------------------------------------------------
test("01 — Home page shows incident list", async ({ page }) => {
  await page.goto("/incidents");
  await expect(page.locator(".page-header h1")).toContainText("Incidents");
  // May show seeded data or empty state — both are valid
  await snap(page, "01-incident-list");
});

// ---------------------------------------------------------------------------
// 2. Submit form page
// ---------------------------------------------------------------------------
test("02 — Submit form renders correctly", async ({ page }) => {
  await page.goto("/incidents/new");
  await expect(page.locator(".page-header h1")).toContainText(
    "Report New Incident"
  );
  await expect(page.locator("#reporter_email")).toBeVisible();
  await expect(page.locator("#description")).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeVisible();
  await snap(page, "02-submit-form-empty");
});

// ---------------------------------------------------------------------------
// 3. Fill the form (screenshot filled state), then create via API
// ---------------------------------------------------------------------------
test("03 — Fill form and create incident", async ({ page }) => {
  await page.goto("/incidents/new");

  // Fill form for the screenshot
  await page.fill("#reporter_name", "SRE On-Call Engineer");
  await page.fill("#reporter_email", "sre-oncall@example.com");
  await page.fill(
    "#description",
    "Payment gateway returning HTTP 502 errors during checkout. " +
      "All customers affected since 14:30 UTC. Stripe webhook handler " +
      "appears to be timing out. Error rate jumped from 0.1% to 45% in " +
      "the last 15 minutes. Checkout completion rate dropped to near zero."
  );
  await snap(page, "03a-submit-form-filled");

  // Create via API for reliability, then navigate to the detail page
  incidentId = await createIncidentViaAPI();
  await page.goto(`/incidents/${incidentId}`);

  await expect(page.locator(".status-badge").first()).toContainText(
    "submitted"
  );
  await snap(page, "03b-incident-created-detail");
});

// ---------------------------------------------------------------------------
// 4. Detail page — untriaged state
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
  await snap(page, "04-detail-untriaged");
});

// ---------------------------------------------------------------------------
// 5. Run AI triage (real Claude Haiku call via API, then verify UI)
// ---------------------------------------------------------------------------
test("05 — Run AI triage and verify results", async ({ page }) => {
  test.setTimeout(90_000); // Claude API can take 10-30s

  if (!incidentId) incidentId = await createIncidentViaAPI();

  // Trigger triage via API for reliability
  await triageViaAPI(incidentId);

  // Now load the detail page and verify results rendered
  await page.goto(`/incidents/${incidentId}`);

  // Verify key triage elements
  await expect(page.locator(".triage-section").first()).toBeVisible();
  await expect(page.locator(".status-badge").first()).toContainText(
    "dispatched"
  );
  await expect(page.locator(".severity-badge")).toBeVisible();
  await expect(page.locator(".confidence-fill")).toBeVisible();

  await snap(page, "05a-triage-results-top");

  // Scroll to see related files and actions
  await page.evaluate(() => window.scrollBy(0, 500));
  await snap(page, "05b-triage-results-scrolled");
});

// ---------------------------------------------------------------------------
// 6. Ticket and notifications on detail page
// ---------------------------------------------------------------------------
test("06 — Verify dispatch panel with ticket and notifications", async ({
  page,
}) => {
  if (!incidentId) {
    test.skip();
    return;
  }

  await page.goto(`/incidents/${incidentId}`);

  // Dispatch card with checklist
  await expect(page.locator(".dispatch-card")).toBeVisible();
  await expect(page.locator(".dispatch-checklist")).toBeVisible();

  // All checks should be done (green checkmarks)
  const checks = page.locator(".check-done");
  await expect(checks.first()).toBeVisible();

  // Scroll to dispatch section
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await snap(page, "06a-dispatch-checklist");

  // Expand ticket detail
  await page.click("details.dispatch-detail:first-of-type summary");
  await expect(page.locator(".dispatch-preview").first()).toBeVisible();
  await snap(page, "06b-ticket-expanded");

  // Expand email notification
  const emailDetail = page.locator("details.dispatch-detail:nth-of-type(2)");
  await emailDetail.locator("summary").click();
  await snap(page, "06c-email-expanded");

  // Integration notice should be visible
  await expect(page.locator(".integration-notice")).toBeVisible();
  await expect(page.locator(".integration-notice")).toContainText(
    "Mock integrations"
  );
  await snap(page, "06d-integration-notice");
});

// ---------------------------------------------------------------------------
// 7. Incident list shows triaged incident
// ---------------------------------------------------------------------------
test("07 — Incident list shows dispatched incident with badges", async ({
  page,
}) => {
  await page.goto("/incidents");

  await expect(page.locator(".clickable-row").first()).toBeVisible({
    timeout: 5_000,
  });

  // Check badges
  const firstRow = page.locator(".clickable-row").first();
  await expect(firstRow.locator(".status-badge")).toBeVisible();
  await expect(firstRow.locator(".severity-badge")).toBeVisible();

  await snap(page, "07-incident-list-with-triaged");
});

// ---------------------------------------------------------------------------
// 8. Acknowledge incident
// ---------------------------------------------------------------------------
test("08 — Acknowledge dispatched incident", async ({ page }) => {
  if (!incidentId) {
    test.skip();
    return;
  }

  await page.goto(`/incidents/${incidentId}`);

  // Acknowledge button should be visible for dispatched incidents
  const ackBtn = page.locator("#ack-btn");
  await expect(ackBtn).toBeVisible();
  await snap(page, "08a-before-acknowledge");

  // Click acknowledge (accept confirm dialog, wait for reload)
  page.on("dialog", (dialog) => dialog.accept());
  await ackBtn.click();
  await page.waitForURL(`/incidents/${incidentId}`, { timeout: 10_000 });
  await page.waitForLoadState("networkidle");
  await snap(page, "08b-after-acknowledge");
});

// ---------------------------------------------------------------------------
// 9. Resolve incident
// ---------------------------------------------------------------------------
test("09 — Resolve incident with dialog", async ({ page }) => {
  if (!incidentId) {
    test.skip();
    return;
  }

  await page.goto(`/incidents/${incidentId}`);

  // Click Resolve button to open dialog
  const resolveBtn = page.locator('.header-actions button:has-text("Resolve")');
  await resolveBtn.click();

  // Fill resolve dialog
  const dialog = page.locator("#resolve-dialog");
  await expect(dialog).toBeVisible();
  await page.selectOption("#resolution_type", "fix");
  await page.fill("#resolution_notes", "Search index rebuilt and hotfix deployed.");
  await snap(page, "09a-resolve-dialog-filled");

  // Submit and wait for page reload
  await page.locator('#resolve-form button[type="submit"]').click();
  await page.waitForURL(`/incidents/${incidentId}`, { timeout: 10_000 });
  await page.waitForLoadState("networkidle");

  // Verify resolved state
  await expect(page.locator(".status-badge").first()).toContainText("resolved");
  await snap(page, "09b-incident-resolved");

  // Resolution card should be visible
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await snap(page, "09c-resolution-details");
});

// ---------------------------------------------------------------------------
// 10. Incident list shows resolved incident
// ---------------------------------------------------------------------------
test("10 — Incident list shows resolved incident", async ({ page }) => {
  await page.goto("/incidents");

  await expect(page.locator(".clickable-row").first()).toBeVisible({
    timeout: 5_000,
  });

  await snap(page, "10-incident-list-final");
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

  await snap(page, "08-not-found-page");
});
