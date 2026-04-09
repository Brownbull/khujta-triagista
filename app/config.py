from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://sre:sre_password@postgres:5432/sre_triage"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Triage provider: "anthropic", "langchain", or "managed"
    triage_provider: str = "anthropic"

    # Anthropic
    anthropic_api_key: str = ""  # Validated at startup for non-dev envs

    # Google (for LangChain provider)
    google_api_key: str = ""

    # Groq (for LangChain provider fallback)
    groq_api_key: str = ""

    # Managed Agents (Experimental engine)
    managed_agent_id: str = ""
    managed_environment_id: str = ""

    # Langfuse
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "http://langfuse:3000"

    # OpenTelemetry
    otel_service_name: str = "sre-triage-agent"

    # Uploads
    upload_dir: str = "/app/uploads"
    max_upload_size_mb: int = 5

    # E-commerce codebase
    ecommerce_repo_path: str = "/app/ecommerce-repo"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
