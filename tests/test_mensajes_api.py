"""Tests HTTP: mensajes 1:1 (POST, GET conversación paginado)."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_post_mensaje_y_aparece_en_conversacion(
    async_client: httpx.AsyncClient, two_user_ids
):
    uid_a, uid_b = two_user_ids
    r_post = await async_client.post(
        "/mensajes",
        json={
            "remitente_id": uid_a,
            "destinatario_id": uid_b,
            "contenido": "Hola desde pytest",
        },
    )
    assert r_post.status_code == 200, r_post.text
    sent = r_post.json()
    assert "id" in sent

    r_conv = await async_client.get(
        f"/mensajes/conversacion/{uid_a}/{uid_b}",
        params={"limit": 20},
    )
    assert r_conv.status_code == 200, r_conv.text
    envelope = r_conv.json()
    assert "items" in envelope
    assert "limit" in envelope
    assert "next_before_id" in envelope
    contents = [m.get("contenido") for m in envelope["items"]]
    assert "Hola desde pytest" in contents


@pytest.mark.asyncio
async def test_conversacion_simetrica_mismo_hilo(
    async_client: httpx.AsyncClient, two_user_ids
):
    uid_a, uid_b = two_user_ids
    r1 = await async_client.get(
        f"/mensajes/conversacion/{uid_a}/{uid_b}", params={"limit": 5}
    )
    r2 = await async_client.get(
        f"/mensajes/conversacion/{uid_b}/{uid_a}", params={"limit": 5}
    )
    assert r1.status_code == 200 and r2.status_code == 200
    ids1 = {m["_id"] for m in r1.json()["items"]}
    ids2 = {m["_id"] for m in r2.json()["items"]}
    assert ids1 == ids2
