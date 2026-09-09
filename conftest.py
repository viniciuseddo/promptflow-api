from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import build_engine, get_db
from app.main import create_app


@pytest.fixture
def client(tmp_path) -> Generator[TestClient, None, None]:
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    test_engine = build_engine(database_url)
    testing_session = sessionmaker(
        bind=test_engine, autoflush=False, expire_on_commit=False
    )
    Base.metadata.create_all(bind=test_engine)
    test_settings = Settings(database_url=database_url, llm_provider="local")

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    application = create_app(initialize_database=False)
    application.dependency_overrides[get_db] = override_get_db
    application.dependency_overrides[get_settings] = lambda: test_settings

    with TestClient(application) as test_client:
        yield test_client

    application.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def template_payload() -> dict:
    return {
        "name": "Descrição de produto",
        "description": "Gera descrições curtas para e-commerce.",
        "system_prompt": "Você é um redator de e-commerce.",
        "user_prompt_template": (
            "Crie uma descrição de {{produto}} para o público {{publico}}."
        ),
        "model": "demo-model",
        "temperature": 0.4,
        "active": True,
    }

