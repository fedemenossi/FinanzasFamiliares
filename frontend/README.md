# Frontend Next.js

Frontend profesional para Asistente Financiero Familiar IA.

## Stack

- Next.js App Router
- React
- TypeScript estricto
- TailwindCSS
- shadcn/ui compatible
- Recharts
- React Hook Form
- Zod
- Axios
- JWT en localStorage

## Variables

Crear `frontend/.env`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

En Railway, configurar la misma variable apuntando al backend publico:

```env
NEXT_PUBLIC_API_URL=https://TU-BACKEND.up.railway.app/api/v1
```

## Desarrollo local

```bash
cd frontend
npm install
npm run dev
```

Abrir:

```text
http://localhost:3000
```

El backend FastAPI debe estar corriendo en:

```text
http://localhost:8000
```

## Build

```bash
npm run build
npm run start
```

## Rutas

- `/login`
- `/register`
- `/dashboard`
- `/uploads`
- `/transactions`
- `/income`
- `/expenses`
- `/categories`
- `/settings`

## Mapeo contra FastAPI actual

El prompt describe endpoints futuros como `/uploads/pdf` o `/income`. El backend actual expone:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /files/upload`
- `GET /files`
- `GET /transactions`
- `PATCH /transactions/:id`
- `GET /categories`
- `GET /manual/income`
- `POST /manual/income`
- `GET /manual/expenses`
- `POST /manual/expenses`
- `GET /dashboard/summary`
- `GET /insights`
- `GET /budgets`
- `POST /budgets`

Los servicios del frontend usan esas rutas reales para no modificar backend.

## Pendientes dependientes del backend

Estas acciones quedan preparadas o visibles a nivel de arquitectura, pero requieren endpoints FastAPI nuevos:

- `DELETE /transactions/:id`
- `POST /categories`
- `PATCH /income/:id`
- `DELETE /income/:id`
- `PATCH /expenses/:id`
- `DELETE /expenses/:id`
