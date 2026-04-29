"""Tests HTTP: agenda de contactos (crear, listar, patch, delete)."""

from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_contacto_crear_listar_patch_eliminar(
    async_client: httpx.AsyncClient, two_user_ids
):
    owner_id, _ = two_user_ids

    r_create = await async_client.post(
        f"/usuarios/{owner_id}/contactos",
        json={
            "nombre": "Juan Pérez",
            "codigo_pais": "+57",
            "numero": "3001234567",
        },
    )
    assert r_create.status_code == 201, r_create.text
    c = r_create.json()
    cid = c["_id"]
    assert c["nombre"] == "Juan Pérez"
    assert c["telefono_e164"] == "+573001234567"

    r_list = await async_client.get(f"/usuarios/{owner_id}/contactos")
    assert r_list.status_code == 200
    assert any(x["_id"] == cid for x in r_list.json())

    r_patch = await async_client.patch(
        f"/usuarios/{owner_id}/contactos/{cid}",
        json={"nombre": "Juan P. Actualizado"},
    )
    assert r_patch.status_code == 200, r_patch.text
    assert r_patch.json()["nombre"] == "Juan P. Actualizado"

    r_del = await async_client.delete(f"/usuarios/{owner_id}/contactos/{cid}")
    assert r_del.status_code == 204

    r_get404 = await async_client.get(f"/usuarios/{owner_id}/contactos")
    assert r_get404.status_code == 200
    assert not any(x["_id"] == cid for x in r_get404.json())
