"""Tests HTTP: grupos, miembros, mensajes de grupo y caso no miembro."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_flujo_grupo_miembros_y_mensajes(
    async_client: httpx.AsyncClient, two_user_ids
):
    uid_a, uid_b = two_user_ids

    r_create = await async_client.post(
        "/grupos",
        json={"nombre": "Grupo Pytest", "creado_por": uid_a},
    )
    assert r_create.status_code == 200, r_create.text
    grupo = r_create.json()
    gid = grupo["id"]
    assert grupo["nombre"] == "Grupo Pytest"

    r_list = await async_client.get("/grupos", params={"usuario_id": uid_a})
    assert r_list.status_code == 200
    gids = {g["_id"] for g in r_list.json()}
    assert gid in gids

    r_get = await async_client.get(f"/grupos/{gid}")
    assert r_get.status_code == 200
    assert r_get.json()["_id"] == gid

    r_mem0 = await async_client.get(f"/grupos/{gid}/miembros")
    assert r_mem0.status_code == 200
    miembros_ini = r_mem0.json()
    assert len(miembros_ini) == 1
    assert miembros_ini[0]["usuario_id"] == uid_a

    r_add = await async_client.post(
        f"/grupos/{gid}/miembros",
        json={"usuario_id": uid_b, "actor_id": uid_a},
    )
    assert r_add.status_code == 200, r_add.text

    r_mem1 = await async_client.get(f"/grupos/{gid}/miembros")
    assert r_mem1.status_code == 200
    uids = {m["usuario_id"] for m in r_mem1.json()}
    assert uids == {uid_a, uid_b}

    r_msg = await async_client.post(
        f"/grupos/{gid}/mensajes",
        json={"remitente_id": uid_b, "contenido": "Hola grupo"},
    )
    assert r_msg.status_code == 200, r_msg.text
    assert "id" in r_msg.json()

    r_hist = await async_client.get(
        f"/grupos/{gid}/mensajes", params={"limit": 10}
    )
    assert r_hist.status_code == 200
    env = r_hist.json()
    textos = [m.get("contenido") for m in env["items"]]
    assert "Hola grupo" in textos


@pytest.mark.asyncio
async def test_post_mensaje_grupo_no_miembro_403(
    async_client: httpx.AsyncClient, two_user_ids
):
    uid_a, uid_b = two_user_ids

    r_create = await async_client.post(
        "/grupos",
        json={"nombre": "Grupo solo A", "creado_por": uid_a},
    )
    assert r_create.status_code == 200
    gid = r_create.json()["id"]

    r_forbidden = await async_client.post(
        f"/grupos/{gid}/mensajes",
        json={"remitente_id": uid_b, "contenido": "intruso"},
    )
    assert r_forbidden.status_code == 403
