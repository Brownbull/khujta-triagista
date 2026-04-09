"""Seed Langfuse with a dev account, organization, project, and API keys.

Runs at startup in development mode. Uses the Langfuse HTTP API to create a
deterministic dev account. Works with Langfuse v2.95+ (org-based project model).

Credentials:
  - Email: admin@sre-triage.local
  - Password: admin123
  - Dashboard: http://localhost:3100
"""

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

LANGFUSE_EMAIL = "admin@sre-triage.local"
LANGFUSE_PASSWORD = "admin123"
LANGFUSE_ORG_NAME = "SRE Triage Agent"
LANGFUSE_PROJECT_NAME = "SRE Triage Agent"


def _trpc_query(host: str, session_cookie: str, path: str, input_data=None) -> dict | None:
    """Execute a tRPC query (GET) with optional input."""
    url = f"{host}/api/trpc/{path}?batch=1"
    if input_data is not None:
        encoded = urllib.parse.quote(json.dumps({"0": {"json": input_data}}))
        url += f"&input={encoded}"
    else:
        url += "&input=%7B%220%22%3A%7B%22json%22%3Anull%7D%7D"
    req = urllib.request.Request(url, headers={"Cookie": session_cookie})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())[0]["result"]["data"]["json"]


def _trpc_mutate(host: str, session_cookie: str, path: str, data: dict) -> dict | None:
    """Execute a tRPC mutation (POST)."""
    payload = json.dumps({"0": {"json": data}}).encode()
    req = urllib.request.Request(
        f"{host}/api/trpc/{path}?batch=1",
        data=payload,
        headers={"Cookie": session_cookie, "Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())[0]["result"]["data"]["json"]


def seed_langfuse(langfuse_host: str) -> dict[str, str] | None:
    """Create Langfuse dev account, org, project, and return API keys.

    Returns {"public_key": ..., "secret_key": ...} or None if already set up.
    """
    # 1. Check if Langfuse is reachable
    try:
        resp = urllib.request.urlopen(f"{langfuse_host}/api/public/health", timeout=5)
        health = json.loads(resp.read())
        if health.get("status") != "OK":
            logger.warning("Langfuse health check failed")
            return None
    except Exception:
        logger.info("Langfuse not reachable at %s — skipping seed", langfuse_host)
        return None

    # 2. Create user (idempotent — ignores error if exists)
    try:
        signup_data = json.dumps({
            "name": "SRE Admin",
            "email": LANGFUSE_EMAIL,
            "password": LANGFUSE_PASSWORD,
        }).encode()
        req = urllib.request.Request(
            f"{langfuse_host}/api/auth/signup",
            data=signup_data,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req)
        logger.info("Langfuse user created: %s", LANGFUSE_EMAIL)
    except urllib.error.HTTPError:
        logger.debug("Langfuse user already exists")
    except Exception:
        logger.warning("Langfuse signup failed", exc_info=True)
        return None

    # 3. Sign in to get session cookie
    try:
        resp = urllib.request.urlopen(f"{langfuse_host}/api/auth/csrf")
        csrf = json.loads(resp.read())["csrfToken"]
        cookies = resp.headers.get_all("Set-Cookie") or []
        cookie_jar = "; ".join(c.split(";")[0] for c in cookies)

        login_data = urllib.parse.urlencode({
            "csrfToken": csrf,
            "email": LANGFUSE_EMAIL,
            "password": LANGFUSE_PASSWORD,
            "json": "true",
        }).encode()
        req = urllib.request.Request(
            f"{langfuse_host}/api/auth/callback/credentials",
            data=login_data,
            headers={"Cookie": cookie_jar, "Content-Type": "application/x-www-form-urlencoded"},
        )
        resp = urllib.request.urlopen(req)
        new_cookies = resp.headers.get_all("Set-Cookie") or []
        session_cookie = "; ".join(c.split(";")[0] for c in new_cookies)
    except Exception:
        logger.warning("Langfuse sign-in failed", exc_info=True)
        return None

    # 4. Check session for existing organizations
    try:
        req = urllib.request.Request(
            f"{langfuse_host}/api/auth/session",
            headers={"Cookie": session_cookie},
        )
        resp = urllib.request.urlopen(req)
        session = json.loads(resp.read())
        orgs = session.get("user", {}).get("organizations", [])
    except Exception:
        orgs = []

    # 5. Create organization if needed
    org_id = None
    if orgs:
        org_id = orgs[0]["id"]
        logger.info("Langfuse org already exists: %s", org_id)
    else:
        try:
            result = _trpc_mutate(
                langfuse_host, session_cookie, "organizations.create",
                {"name": LANGFUSE_ORG_NAME},
            )
            org_id = result["id"]
            logger.info("Langfuse org created: %s", org_id)
        except Exception:
            logger.warning("Langfuse org creation failed", exc_info=True)
            return None

    # 6. Check for existing projects (re-read session after org creation)
    project_id = None
    try:
        req = urllib.request.Request(
            f"{langfuse_host}/api/auth/session",
            headers={"Cookie": session_cookie},
        )
        resp = urllib.request.urlopen(req)
        session = json.loads(resp.read())
        orgs = session.get("user", {}).get("organizations", [])
        for org in orgs:
            for proj in org.get("projects", []):
                project_id = proj["id"]
                logger.info("Langfuse project already exists: %s", project_id)
                break
            if project_id:
                break
    except Exception:
        logger.debug("Could not check existing projects")

    # 7. Create project if needed
    if not project_id:
        try:
            result = _trpc_mutate(
                langfuse_host, session_cookie, "projects.create",
                {"name": LANGFUSE_PROJECT_NAME, "orgId": org_id},
            )
            project_id = result["id"]
            logger.info("Langfuse project created: %s", project_id)
        except Exception:
            logger.warning("Langfuse project creation failed", exc_info=True)
            return None

    # 8. Create API keys (always — secret is only returned at creation time)
    # Langfuse allows multiple key pairs per project. We create a new one each
    # startup because the secret key from previous runs is not retrievable.
    try:
        key_data = _trpc_mutate(
            langfuse_host, session_cookie, "apiKeys.create",
            {"projectId": project_id, "note": "auto-seeded-dev"},
        )
        public_key = key_data["publicKey"]
        secret_key = key_data["secretKey"]
        logger.info("Langfuse API keys created: pk=%s", public_key)
        return {"public_key": public_key, "secret_key": secret_key}
    except Exception:
        logger.warning("Langfuse API key creation failed", exc_info=True)
        return None
