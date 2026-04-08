"""Seed data for development — pre-populates the database with sample incidents.

Only runs when APP_ENV=development and the incidents table is empty.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident, IncidentStatus, Severity
from app.models.notification import Notification, NotificationType
from app.models.ticket import Ticket, TicketStatus

logger = logging.getLogger(__name__)

SEED_INCIDENTS = [
    {
        "reporter_name": "Maria Chen",
        "reporter_email": "maria.chen@example.com",
        "description": (
            "Payment gateway returning HTTP 502 errors during checkout. "
            "All customers affected since 14:30 UTC. Stripe webhook handler "
            "appears to be timing out. Error rate jumped from 0.1% to 45% in "
            "the last 15 minutes. Checkout completion rate dropped to near zero."
        ),
        "status": IncidentStatus.DISPATCHED,
        "severity": Severity.P1,
        "category": "payment-processing",
        "affected_component": "Stripe webhook handler, Spree::Payment gateway",
        "technical_summary": (
            "Critical payment gateway failure causing HTTP 502 errors during checkout. "
            "The Stripe webhook handler is timing out, preventing order confirmation. "
            "Error rate spiked from 0.1% to 45% in 15 minutes, with checkout completion "
            "dropping to near zero. The root cause appears to be in the webhook "
            "acknowledgment pipeline where synchronous database operations are blocking "
            "the response timeout."
        ),
        "root_cause_hypothesis": (
            "Stripe webhook handler timeout caused by synchronous database writes "
            "during webhook processing. A recent deployment likely introduced a "
            "blocking query in the payment confirmation path."
        ),
        "suggested_assignee": "payments-team",
        "confidence": 0.88,
        "recommended_actions": [
            "Check Stripe dashboard for webhook delivery failures since 14:30 UTC",
            "Review recent deployments affecting payment or webhook code",
            "Verify database connection pool is not exhausted",
            "Consider adding circuit breaker to payment gateway calls",
        ],
        "related_files": [
            {"path": "core/app/models/spree/payment.rb", "relevance": "Payment model with gateway delegation"},
            {"path": "core/app/models/spree/payment_method.rb", "relevance": "Gateway interface definition"},
            {"path": "backend/app/controllers/spree/admin/payments_controller.rb", "relevance": "Payment processing controller"},
        ],
        "ticket": {
            "title": "[P1] payment-processing: Payment gateway returning HTTP 502 errors",
            "assignee": "payments-team",
            "labels": {"severity": "P1", "category": "payment-processing"},
        },
        "notifications": [
            {"type": NotificationType.EMAIL, "recipient": "payments-oncall@example.com",
             "subject": "[P1] New incident: Payment gateway 502 errors", "body": "Critical payment outage..."},
            {"type": NotificationType.CHAT, "recipient": "#incidents",
             "subject": None, "body": "❗ *P1 Incident* — payment-processing\nComponent: Stripe webhook handler"},
        ],
    },
    {
        "reporter_name": "James Park",
        "reporter_email": "james.park@example.com",
        "description": (
            "Product search returning zero results for all queries since the "
            "latest deploy at 09:15 UTC. The search index appears to be empty "
            "or disconnected. Customers cannot find any products. Verified on "
            "staging — works fine there."
        ),
        "status": IncidentStatus.DISPATCHED,
        "severity": Severity.P2,
        "category": "storefront",
        "affected_component": "Spree::Product search, Solidus search index",
        "technical_summary": (
            "Product search is returning empty results across the entire storefront. "
            "The issue started after a deploy at 09:15 UTC and is limited to production "
            "(staging works fine). This suggests a configuration or data issue rather "
            "than a code bug — likely the search index was not rebuilt after the deploy."
        ),
        "root_cause_hypothesis": (
            "Search index not rebuilt after latest deployment. The deploy may have "
            "reset or corrupted the product index without triggering a reindex job."
        ),
        "suggested_assignee": "platform-team",
        "confidence": 0.79,
        "recommended_actions": [
            "Trigger a full reindex of the product catalog",
            "Check if the deploy script includes a reindex step",
            "Verify search service connectivity in production",
        ],
        "related_files": [
            {"path": "core/app/models/spree/product.rb", "relevance": "Product model with search scopes"},
            {"path": "core/lib/spree/core/search/base.rb", "relevance": "Search implementation"},
        ],
        "ticket": {
            "title": "[P2] storefront: Product search returning zero results",
            "assignee": "platform-team",
            "labels": {"severity": "P2", "category": "storefront"},
        },
        "notifications": [
            {"type": NotificationType.EMAIL, "recipient": "platform-oncall@example.com",
             "subject": "[P2] New incident: Search returning zero results", "body": "Search outage..."},
            {"type": NotificationType.CHAT, "recipient": "#incidents",
             "subject": None, "body": "⚠️ *P2 Incident* — storefront\nComponent: Product search"},
        ],
    },
    {
        "reporter_name": "Sarah Kim",
        "reporter_email": "sarah.kim@example.com",
        "description": (
            "Admin panel showing 403 Forbidden for all non-super-admin users since "
            "the permission migration ran this morning. Store managers cannot access "
            "order management. Roughly 15 admin users affected."
        ),
        "status": IncidentStatus.SUBMITTED,
        "severity": None,
        "category": None,
        "affected_component": None,
        "technical_summary": None,
        "root_cause_hypothesis": None,
        "suggested_assignee": None,
        "confidence": None,
        "recommended_actions": None,
        "related_files": None,
        "ticket": None,
        "notifications": [],
    },
    {
        "reporter_name": None,
        "reporter_email": "ops@example.com",
        "description": (
            "Intermittent 504 Gateway Timeout on product detail pages during peak "
            "hours (12:00-14:00 UTC). Affects roughly 5% of requests. Response times "
            "spike from 200ms to 8s. Seems related to variant pricing calculations "
            "on products with 50+ variants."
        ),
        "status": IncidentStatus.SUBMITTED,
        "severity": None,
        "category": None,
        "affected_component": None,
        "technical_summary": None,
        "root_cause_hypothesis": None,
        "suggested_assignee": None,
        "confidence": None,
        "recommended_actions": None,
        "related_files": None,
        "ticket": None,
        "notifications": [],
    },
]


async def seed_database(db: AsyncSession) -> None:
    """Populate the database with sample incidents if empty."""
    count_result = await db.execute(select(func.count(Incident.id)))
    existing = count_result.scalar_one()

    if existing > 0:
        logger.info("Database already has %d incidents — skipping seed", existing)
        return

    logger.info("Seeding database with %d sample incidents...", len(SEED_INCIDENTS))

    for data in SEED_INCIDENTS:
        incident = Incident(
            reporter_name=data["reporter_name"],
            reporter_email=data["reporter_email"],
            description=data["description"],
            status=data["status"],
            severity=data["severity"],
            category=data["category"],
            affected_component=data["affected_component"],
            technical_summary=data["technical_summary"],
            root_cause_hypothesis=data["root_cause_hypothesis"],
            suggested_assignee=data["suggested_assignee"],
            confidence=data["confidence"],
            recommended_actions=data["recommended_actions"],
            related_files=data["related_files"],
        )
        db.add(incident)
        await db.flush()

        # Create ticket if triaged
        if data["ticket"]:
            ticket = Ticket(
                incident_id=incident.id,
                title=data["ticket"]["title"],
                body=f"## Technical Summary\n\n{data['technical_summary']}",
                status=TicketStatus.OPEN,
                labels=data["ticket"]["labels"],
                assignee=data["ticket"]["assignee"],
            )
            db.add(ticket)

        # Create notifications
        for notif_data in data["notifications"]:
            notif = Notification(
                incident_id=incident.id,
                type=notif_data["type"],
                recipient=notif_data["recipient"],
                subject=notif_data["subject"],
                body=notif_data["body"],
                sent=True,
                sent_at=datetime.now(timezone.utc),
            )
            db.add(notif)

    await db.commit()
    logger.info("Seed complete: %d incidents created", len(SEED_INCIDENTS))
