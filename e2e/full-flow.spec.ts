import { test, expect, Page } from "@playwright/test";
import path from "path";

const SCREENSHOTS = path.join(__dirname, "screenshots");
const BASE = "http://localhost:8100";

// Shared state across serial tests
let incidentId: string;

// Helper: save a named screenshot
async function snap(page: Page, name: string) {
  await page.screenshot({
    path: path.join(SCREENSHOTS, `${name}.png`),
    fullPage: true,
  });
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

// Helper: triage incident via API (reliable)
async function triageViaAPI(id: string): Promise<void> {
  await fetch(`${BASE}/api/incidents/${id}/triage`, { method: "POST" });
}

// ---------------------------------------------------------------------------
// 1. Empty state
// ---------------------------------------------------------------------------
test("01 — Home page shows empty state", async ({ page }) => {
  await page.goto("/incidents");
  await expect(page.locator(".page-header h1")).toContainText("Incidents");
  await expect(page.locator(".empty-state h1")).toContainText(
    "No incidents yet"
  );
  await snap(page, "01-empty-incident-list");
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
test("06 — Verify ticket and notifications are displayed", async ({
  page,
}) => {
  if (!incidentId) {
    test.skip();
    return;
  }

  await page.goto(`/incidents/${incidentId}`);

  // Ticket card
  await expect(page.locator(".ticket-card")).toBeVisible();
  await expect(page.locator(".ticket-card")).toContainText("Ticket");

  // Notifications card
  await expect(page.locator(".notifications-card")).toBeVisible();
  await expect(page.locator(".notifications-card")).toContainText("email");
  await expect(page.locator(".notifications-card")).toContainText("chat");
  await expect(page.locator(".notifications-card")).toContainText("sent");

  // Scroll to bottom to capture ticket + notifications
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await snap(page, "06-ticket-and-notifications");
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
// 8. 404 page
// ---------------------------------------------------------------------------
test("08 — 404 page for non-existent incident", async ({ page }) => {
  await page.goto("/incidents/00000000-0000-0000-0000-000000000000");

  await expect(page.locator(".empty-state h1")).toContainText("Not Found");
  await expect(
    page.locator('a:has-text("View All Incidents")')
  ).toBeVisible();

  await snap(page, "08-not-found-page");
});
