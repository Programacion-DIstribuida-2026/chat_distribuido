"""Tests HTTP: usuarios (POST, GET lista, GET por id, 404)."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_post_usuario_devuelve_id_y_nombre(async_client: httpx.AsyncClient):
    r = await async_client.post("/usuarios", json={"nombre": "Usuario REST"})
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert data["nombre"] == "Usuario REST"
    assert len(data["id"]) == 24


@pytest.mark.asyncio
async def test_get_usuario_por_id(async_client: httpx.AsyncClient, two_user_ids):
    uid_a, _ = two_user_ids
    r = await async_client.get(f"/usuarios/{uid_a}")
    assert r.status_code == 200
    data = r.json()
    assert data["_id"] == uid_a
    assert data["nombre"] == "Pytest Usuario A"


@pytest.mark.asyncio
async def test_get_usuario_inexistente_404(async_client: httpx.AsyncClient):
    oid = "000000000000000000000001"
    r = await async_client.get(f"/usuarios/{oid}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_listar_usuarios_incluye_creados(
    async_client: httpx.AsyncClient, two_user_ids
):
    uid_a, uid_b = two_user_ids
    r = await async_client.get("/usuarios")
    assert r.status_code == 200
    users = r.json()
    ids = {u["_id"] for u in users}
    assert uid_a in ids
    assert uid_b in ids
