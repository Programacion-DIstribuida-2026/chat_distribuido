# Chat Distribuido

API REST + WebSocket en tiempo real con FastAPI y MySQL. Dos personas chatean conectando cada una con **su ID** y el **ID del otro** en la interfaz web.

## Requisitos

- Python 3.12+
- Docker (Docker Compose)

## Puesta en marcha

### 1. Base de datos

Desde la raíz del proyecto:

```bash
docker compose up -d db
```

Esto expone MySQL en el puerto **3380** (usuario `user`, contraseña `123`, base `chat_db`), igual que espera `database.py`.

Opcional: levantar también phpMyAdmin en http://127.0.0.1:8080:

```bash
docker compose up -d
```

### 2. Entorno Python

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. API

```bash
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

- Documentación interactiva: http://127.0.0.1:9000/docs  
- **Chat en el navegador:** http://127.0.0.1:9000/chat (solo en el mismo PC que corre el servidor).

### 4. Probar el chat entre dos personas

1. En **/docs**, `POST /usuarios` dos veces (por ejemplo nombres "Ana" y "Beto"). La respuesta incluye **`id`** de cada usuario.
2. **Mismo PC, dos pestañas:** abre dos veces http://127.0.0.1:9000/chat.
3. **Otro móvil u ordenador en tu Wi‑Fi/LAN:** deben abrir **`http://<IP_DE_TU_EQUIPO>:9000/chat`**, no `127.0.0.1`. La `127.0.0.1` en *su* navegador apunta a *su* máquina, no a la tuya. Obtén tu IP con `ip a` / `hostname -I` (Linux), `ipconfig` (Windows, busca IPv4 en la red Wi‑Fi).
4. En el firewall de quien ejecuta el servidor, permite conexiones entrantes al **puerto 9000** (TCP).
5. **Persona A:** Mi ID = id de Ana, Compañero = id de Beto → **Conectar**.  
   **Persona B:** Mi ID = id de Beto, Compañero = id de Ana → **Conectar**.
6. Si alguien abre la página desde un sitio distinto y el WebSocket falla, en `/chat` puede rellenar **“Servidor del chat”** con `TU_IP:9000`.

Los mensajes llegan en tiempo real y se guardan en MySQL (remitente según el esquema actual).

La ruta WebSocket es: `ws://<host>:9000/ws/chat/{mi_id}/{id_del_otro}`.

### 5. WSL2: si `172.16.x.x` “no funciona” desde otro móvil u ordenador

En **WSL2**, la IP que ves con `ip a` o `hostname -I` (muchas veces **172.16.x.x** o **172.x.x.x**) suele ser la **red virtual entre Windows y Linux**, no la Wi‑Fi de tu casa. **Los móviles y otros PCs en tu Wi‑Fi no pueden llegar a esa IP** salvo que reenvíes el puerto en Windows.

**Qué usar en el otro dispositivo:** la **IPv4 de Windows en la Wi‑Fi/Ethernet**, la de `ipconfig` en **PowerShell o CMD** (suele ser `192.168.x.x`), **no** la 172.x de WSL.

**Reenvío de puerto (PowerShell como administrador):**

1. Con Uvicorn ya corriendo en WSL, obtén la IP de WSL:

   ```powershell
   wsl hostname -I
   ```

   Anota la primera IP (ej. `172.16.0.229`).

2. Crea el reenvío del **9000** de Windows hacia WSL (sustituye `WSL_IP`):

   ```powershell
   netsh interface portproxy add v4tov4 listenport=9000 listenaddress=0.0.0.0 connectport=9000 connectaddress=WSL_IP
   ```

3. Abre el puerto en el firewall de Windows:

   ```powershell
   netsh advfirewall firewall add rule name="Chat distribuido 9000" dir=in action=allow protocol=TCP localport=9000
   ```

4. En el **móvil u otro PC**, abre: `http://<IP_DE_WINDOWS_EN_WIFI>:9000/chat` (la de `ipconfig`, no la de WSL).

Si reinicias WSL y cambia su IP, borra la regla antigua y vuelve a crearla:

```powershell
netsh interface portproxy delete v4tov4 listenport=9000 listenaddress=0.0.0.0
```

**Alternativa:** instalar Python en **Windows**, clonar el proyecto en una carpeta de Windows y ejecutar ahí `uvicorn ... --host 0.0.0.0 --port 9000`; entonces el otro dispositivo usa la misma IP de `ipconfig` sin `portproxy`.

### 6. Si “no me funciona” (checklist rápido)

| Síntoma | Qué revisar |
|--------|-------------|
| El otro no abre ni la página | IP correcta (Windows en Wi‑Fi si usas WSL2), firewall, `portproxy` en WSL2 |
| La página carga pero el chat no conecta | En “Servidor del chat” pon `IP_DE_WINDOWS:9000`; ambos deben tener **Conectar** con IDs cruzados |
| Error al enviar / base de datos | MySQL en marcha (`docker compose up -d db`) y variables `DB_*` si no usas el puerto 3380 por defecto |


### Una demostracion como funciona 
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/c38776b2-5584-4941-93c0-d219fb0e5642" />

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /usuarios | Crear usuario (respuesta incluye `id`) |
| GET | /usuarios | Listar usuarios |
| GET | /usuarios/{id} | Obtener usuario por ID |
| POST | /mensajes | Enviar mensaje |
| GET | /mensajes | Ver historial completo |
| GET | /mensajes/{id_usuario} | Ver mensajes por usuario |

## Tecnologías

- FastAPI, Uvicorn, WebSockets  
- aiomysql, MySQL 8.0  
