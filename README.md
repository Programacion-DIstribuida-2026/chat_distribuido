# Chat Distribuido 🗨️

API REST para un sistema de chat centralizado desarrollado con FastAPI y MySQL.

## Requisitos
- Python 3.12+
- Docker Desktop

## Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/Programacion-DIstribuida-2026/chat_distribuido.git
cd chat_distribuido
```

### 2. Levantar la base de datos con Docker
```bash
sudo docker run --name chat_mysql \
  -e MYSQL_ROOT_PASSWORD=123 \
  -e MYSQL_DATABASE=chat_db \
  -e MYSQL_USER=user \
  -e MYSQL_PASSWORD=123 \
  -p 3380:3306 \
  -d mysql:8.0
```

### 3. Crear y activar el entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install fastapi uvicorn aiomysql cryptography
```

### 5. Correr la API
```bash
uvicorn main:app --port 9000 --reload
```

### 6. Documentación
Abre en tu navegador: http://127.0.0.1:9000/docs

## Endpoints
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /usuarios | Crear usuario |
| GET | /usuarios | Listar usuarios |
| GET | /usuarios/{id} | Obtener usuario por ID |
| POST | /mensajes | Enviar mensaje |
| GET | /mensajes | Ver historial completo |
| GET | /mensajes/{id_usuario} | Ver mensajes por usuario |

## Tecnologías
- FastAPI
- aiomysql
- MySQL 8.0 (Docker)
- Python 3.12