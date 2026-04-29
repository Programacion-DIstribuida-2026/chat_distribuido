"""Configuración de pytest: BD `chat_test` y cliente HTTP ASGI con lifespan."""

from __future__ import annotations

import os

os.environ["MONGO_DB_NAME"] = "chat_test"

import httpx
import pytest
import pytest_asyncio
from pymongo import MongoClient

_DEFAULT_MONGO_URL = "mongodb://admin:123@127.0.0.1:37117/?authSource=admin"


@pytest.fixture(scope="session")
def _wipe_test_database():
    """Ping + borrado síncrono: mismo criterio de conexión que los tests HTTP."""
    url = os.environ.get("MONGO_URL", _DEFAULT_MONGO_URL)
    try:
        mc = MongoClient(url, serverSelectionTimeoutMS=5000)
        mc.admin.command("ping")
    except Exception:
        pytest.skip("MongoDB no disponible (comprueba MONGO_URL y docker compose)")
    try:
        if os.environ.get("MONGO_DB_NAME") == "chat_test":
            mc.drop_database("chat_test")
    finally:
        mc.close()
    yield


from main import app  # noqa: E402


@pytest_asyncio.fixture(scope="session")
async def async_client(_wipe_test_database):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def two_user_ids(async_client: httpx.AsyncClient):
    r_a = await async_client.post("/usuarios", json={"nombre": "Pytest Usuario A"})
    r_b = await async_client.post("/usuarios", json={"nombre": "Pytest Usuario B"})
    assert r_a.status_code == 200, r_a.text
    assert r_b.status_code == 200, r_b.text
    ja = r_a.json()
    jb = r_b.json()
    return ja["id"], jb["id"]
