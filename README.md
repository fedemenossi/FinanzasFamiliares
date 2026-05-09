# Asistente Financiero Familiar IA

MVP funcional para procesar resúmenes bancarios argentinos, clasificar gastos familiares y mostrar un dashboard financiero. Incluye backend FastAPI, frontend Streamlit, MySQL 8, SQLAlchemy 2.x, Alembic, parsers PDF y Docker.

## Funcionalidades

- Registro, login y autenticación JWT.
- Subida de PDFs bancarios.
- Detección automática de BBVA Visa Platinum, Banco Nación Visa Signature o parser Visa genérico.
- Extracción de movimientos, importes argentinos y cuotas.
- Clasificación automática por reglas.
- Gastos fijos, variables y excepcionales.
- Registro manual de ingresos y gastos.
- Panel de movimientos con búsqueda y reclasificación.
- Dashboard con KPIs, categorías, evolución mensual, fijos vs variables, top gastos y comercios frecuentes.

## Estructura

```text
backend/
  app/
    api/
    ai/
    core/
    db/
    models/
    parsers/
    schemas/
    services/
  alembic/
frontend/
docker-compose.yml
```

## Deploy en Railway

Este proyecto está preparado para desplegarse como monorepo con dos servicios Railway y una base MySQL.

### 1. Crear proyecto y base

1. Crear un proyecto nuevo en Railway.
2. Agregar un servicio MySQL.
3. Railway expondrá una variable tipo `MYSQL_URL`. El backend la acepta automáticamente y la convierte al driver `mysql+pymysql`.

### 2. Backend

Crear un servicio desde el repositorio con:

- Root Directory: `backend`
- Builder: Dockerfile

Variables recomendadas:

```env
SECRET_KEY=una-clave-larga-y-aleatoria
UPLOAD_DIR=/app/uploads
CORS_ORIGINS=*
MYSQL_URL=${{MySQL.MYSQL_URL}}
```

El `Dockerfile` ejecuta automáticamente:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Cuando Railway publique el backend, probar:

```text
https://TU-BACKEND.up.railway.app/health
https://TU-BACKEND.up.railway.app/docs
```

### 3. Frontend

Crear otro servicio desde el mismo repositorio con:

- Root Directory: `frontend`
- Builder: Dockerfile

Variables:

```env
API_URL=https://TU-BACKEND.up.railway.app/api/v1
```

El frontend escucha el puerto dinámico `$PORT` que Railway asigna.

### 4. Orden de deploy

1. Deploy MySQL.
2. Deploy backend.
3. Verificar `/health`.
4. Deploy frontend con `API_URL` apuntando al backend público.

## Ejecución con Docker local opcional

```bash
docker compose up --build
```

Servicios:

- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Frontend: `http://localhost:8501`
- MySQL: `localhost:3306`

El backend ejecuta `alembic upgrade head` al iniciar.

## Ejecución local sin Docker

1. Crear una base MySQL:

```sql
CREATE DATABASE family_finance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'family'@'%' IDENTIFIED BY 'family';
GRANT ALL PRIVILEGES ON family_finance.* TO 'family'@'%';
```

2. Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

3. Frontend:

```bash
cd frontend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set API_URL=http://localhost:8000/api/v1
streamlit run streamlit_app.py
```

## Variables de entorno

Ver `.env.example`.

- `DATABASE_URL`: URL SQLAlchemy para MySQL.
- `SECRET_KEY`: clave para firmar JWT.
- `UPLOAD_DIR`: carpeta de PDFs subidos.
- `OPENAI_API_KEY`: reservado para clasificación IA futura.
- `CORS_ORIGINS`: orígenes permitidos.
- `API_URL`: URL que usa Streamlit para llamar al backend.

## Migraciones

Crear una migración nueva:

```bash
cd backend
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

## Uso

1. Crear usuario.
2. Registrar ingresos manuales.
3. Subir PDFs bancarios.
4. Revisar movimientos importados.
5. Reclasificar si hace falta.
6. Analizar dashboard.

Los parsers están preparados para líneas habituales de resúmenes Visa argentinos con fechas, descripción, importe y cuotas como `Cuota 06/06`.
