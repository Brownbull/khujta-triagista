from app.models.incident import IncidentStatus, Severity
from app.models.ticket import TicketStatus
from app.models.notification import NotificationType


def test_incident_status_values():
    assert IncidentStatus.SUBMITTED == "submitted"
    assert IncidentStatus.TRIAGING == "triaging"
    assert IncidentStatus.RESOLVED == "resolved"
    assert IncidentStatus.REJECTED == "rejected"


def test_severity_values():
    assert Severity.P1 == "P1"
    assert Severity.P4 == "P4"


def test_ticket_status_values():
    assert TicketStatus.OPEN == "open"
    assert TicketStatus.RESOLVED == "resolved"


def test_notification_type_values():
    assert NotificationType.EMAIL == "email"
    assert NotificationType.CHAT == "chat"
