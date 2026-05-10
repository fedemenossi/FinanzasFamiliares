# Asistente Financiero Familiar IA

Aplicacion fintech familiar para procesar resumenes bancarios argentinos, clasificar gastos y visualizar salud financiera. El backend se mantiene en FastAPI/Python y el frontend fue migrado a Next.js.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic.
- Base de datos: MySQL 8.
- Driver MySQL: `pymysql`.
- PDFs: `pdfplumber` y `PyMuPDF`.
- IA futura: OpenAI API mediante `OPENAI_API_KEY`.
- Frontend: Next.js App Router, React, TypeScript, TailwindCSS, shadcn/ui compatible y Recharts.
- Deploy: Railway.

## Funcionalidades

- Registro, login y autenticacion JWT.
- Dashboard financiero con KPIs y graficos.
- Subida de PDFs bancarios.
- Deteccion de BBVA Visa Platinum, Banco Nacion Visa Signature o parser generico.
- Extraccion de movimientos, importes argentinos y cuotas.
- Clasificacion automatica por reglas.
- Gastos fijos, variables y excepcionales.
- Registro manual de ingresos y gastos.
- Panel de movimientos con busqueda y reclasificacion.
- Presupuestos mensuales por categoria.
- Insights automaticos.
- Deduplicacion basica al reimportar movimientos.

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
  app/
  components/
  hooks/
  lib/
  services/
  types/
docker-compose.yml
```

## Ejecucion local

Usar dos terminales.

### Backend

```powershell
cd D:\Fede\FinanzasFamiliares\backend
.\.venv\Scripts\activate
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verificar:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

### Frontend

Crear `frontend/.env`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Ejecutar:

```powershell
cd D:\Fede\FinanzasFamiliares\frontend
npm install
npm run dev
```

Abrir:

```text
http://localhost:3000
```

## Variables de entorno

Backend, en `backend/.env` o Railway:

```env
DATABASE_URL=
MYSQL_URL=mysql://...
SECRET_KEY=una-clave-larga
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=uploads
OPENAI_API_KEY=
CORS_ORIGINS=*
```

Frontend, en `frontend/.env` o Railway:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

No poner credenciales de base de datos ni secretos en el frontend.

## Railway

Crear un proyecto Railway con tres piezas:

1. Servicio MySQL.
2. Servicio backend con Root Directory `backend`.
3. Servicio frontend con Root Directory `frontend`.

### Backend Railway

Variables:

```env
SECRET_KEY=una-clave-larga-y-aleatoria
UPLOAD_DIR=/app/uploads
CORS_ORIGINS=*
MYSQL_URL=${{MySQL.MYSQL_URL}}
OPENAI_API_KEY=
```

El backend ejecuta automaticamente:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Probar:

```text
https://TU-BACKEND.up.railway.app/health
https://TU-BACKEND.up.railway.app/docs
```

### Frontend Railway

Variable:

```env
NEXT_PUBLIC_API_URL=https://TU-BACKEND.up.railway.app/api/v1
```

El frontend Next.js escucha el puerto dinamico `$PORT`.

## Docker local opcional

```bash
docker compose up --build
```

Servicios:

- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Frontend Next.js: `http://localhost:3000`
- MySQL: `localhost:3306`

## Migraciones

```powershell
cd backend
python -m alembic revision --autogenerate -m "descripcion"
python -m alembic upgrade head
```

En Railway, `alembic upgrade head` corre en cada arranque del backend.

## Uso

1. Crear usuario en `/register`.
2. Ingresar en `/login`.
3. Registrar ingresos.
4. Subir PDFs bancarios.
5. Revisar y reclasificar movimientos.
6. Cargar presupuestos por categoria.
7. Analizar dashboard e insights.

## Estado de endpoints

El frontend consume las rutas reales actuales del backend:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/files/upload`
- `GET /api/v1/transactions`
- `PATCH /api/v1/transactions/:id`
- `GET /api/v1/categories`
- `GET /api/v1/manual/income`
- `POST /api/v1/manual/income`
- `GET /api/v1/manual/expenses`
- `POST /api/v1/manual/expenses`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/insights`
- `GET /api/v1/budgets`
- `POST /api/v1/budgets`

Pendientes para completar CRUD total:

- `DELETE /transactions/:id`
- `POST /categories`
- `PATCH /income/:id`
- `DELETE /income/:id`
- `PATCH /expenses/:id`
- `DELETE /expenses/:id`
