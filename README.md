# Asistente Financiero Familiar IA

MVP funcional para procesar resumenes bancarios argentinos, clasificar gastos familiares y mostrar un dashboard financiero. Incluye backend FastAPI, frontend Streamlit, MySQL 8, SQLAlchemy 2.x, Alembic, parsers PDF y Docker.

## Funcionalidades

- Registro, login y autenticacion JWT.
- Subida de PDFs bancarios.
- Deteccion automatica de BBVA Visa Platinum, Banco Nacion Visa Signature o parser Visa generico.
- Extraccion de movimientos, importes argentinos y cuotas.
- Clasificacion automatica por reglas.
- Gastos fijos, variables y excepcionales.
- Registro manual de ingresos y gastos.
- Panel de movimientos con busqueda y reclasificacion.
- Dashboard con KPIs, categorias, evolucion mensual, fijos vs variables, top gastos y comercios frecuentes.
- Fase 2: presupuestos mensuales por categoria, insights automaticos y deduplicacion al reimportar movimientos.

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

Este proyecto esta preparado para desplegarse como monorepo con dos servicios Railway y una base MySQL.

### 1. Crear proyecto y base

1. Crear un proyecto nuevo en Railway.
2. Agregar un servicio MySQL.
3. Railway expondra una variable tipo `MYSQL_URL`. El backend la acepta automaticamente y la convierte al driver `mysql+pymysql`.

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

El `Dockerfile` ejecuta automaticamente:

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

El frontend escucha el puerto dinamico `$PORT` que Railway asigna.

### 4. Orden de deploy

1. Deploy MySQL.
2. Deploy backend.
3. Verificar `/health`.
4. Deploy frontend con `API_URL` apuntando al backend publico.

## Ejecucion con Docker local opcional

```bash
docker compose up --build
```

Servicios:

- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Frontend: `http://localhost:8501`
- MySQL: `localhost:3306`

El backend ejecuta `alembic upgrade head` al iniciar.

## Ejecucion local sin Docker

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
- `MYSQL_URL`: URL MySQL provista por Railway.
- `SECRET_KEY`: clave para firmar JWT.
- `UPLOAD_DIR`: carpeta de PDFs subidos.
- `OPENAI_API_KEY`: reservado para clasificacion IA futura.
- `CORS_ORIGINS`: origenes permitidos.
- `API_URL`: URL que usa Streamlit para llamar al backend.

## Migraciones

Crear una migracion nueva:

```bash
cd backend
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

En Railway, el backend corre `alembic upgrade head`, por lo que la migracion `0002_phase2_budgets` se aplica automaticamente en el proximo deploy.

## Uso

1. Crear usuario.
2. Registrar ingresos manuales.
3. Subir PDFs bancarios.
4. Revisar movimientos importados.
5. Reclasificar si hace falta.
6. Crear presupuestos por categoria.
7. Analizar dashboard e insights.

Los parsers estan preparados para lineas habituales de resumenes Visa argentinos con fechas, descripcion, importe y cuotas como `Cuota 06/06`.

## Fase 2

La Fase 2 agrega capacidades de control financiero:

- `budgets`: presupuestos mensuales por categoria.
- `GET /api/v1/budgets`: lista presupuestos y calcula gastado, restante y porcentaje de uso.
- `POST /api/v1/budgets`: crea o actualiza el presupuesto de una categoria para un mes.
- `GET /api/v1/insights`: genera alertas de ahorro bajo, carga fija alta, presupuestos excedidos y gastos hormiga.
- Deduplicacion basica en importacion de PDFs por usuario, fecha, descripcion, importe, banco y tipo de tarjeta.
