# Arquitectura

## Vision general

El sistema esta dividido en tres capas:

- Backend FastAPI: API REST, autenticacion, persistencia, procesamiento de PDFs, clasificacion y analisis.
- MySQL 8: datos transaccionales, usuarios, categorias, movimientos, archivos y presupuestos.
- Frontend Next.js: aplicacion web profesional, responsive y orientada a producto fintech.

El backend no fue migrado a Node.js. La migracion fue solo del frontend, reemplazando Streamlit por Next.js.

## Backend

Modulos principales:

- `app/api`: routers HTTP.
- `app/models`: modelos SQLAlchemy 2.x.
- `app/schemas`: contratos Pydantic.
- `app/parsers`: arquitectura extensible de parsers bancarios.
- `app/services`: reglas de clasificacion y bootstrap de categorias.
- `app/ai`: integracion con OpenAI para analizar PDFs ya parseados.

Routers actuales:

- `auth`
- `categories`
- `files`
- `transactions`
- `manual`
- `dashboard`
- `reports`
- `budgets`
- `insights`

## Frontend

El frontend vive en `frontend/` y usa:

- Next.js App Router.
- React.
- TypeScript estricto.
- TailwindCSS.
- Componentes compatibles con shadcn/ui.
- Recharts.
- React Hook Form.
- Zod.
- Axios.
- JWT en localStorage.

Estructura principal:

```text
frontend/
  app/
    login/
    register/
    dashboard/
    consultas/
    uploads/
    transactions/
    income/
    expenses/
    categories/
    settings/
  components/
    charts/
    forms/
    layout/
    ui/
  hooks/
  lib/
  services/
  types/
```

`NEXT_PUBLIC_API_URL` define la URL base del backend.

## Autenticacion

1. El usuario ingresa o se registra desde Next.js.
2. El frontend llama a `POST /api/v1/auth/login`.
3. El backend devuelve un JWT.
4. El frontend guarda el token en `localStorage`.
5. Axios agrega `Authorization: Bearer <token>` en cada request privada.
6. El layout privado valida sesion con `GET /api/v1/auth/me`.

## Flujo de PDFs

1. El usuario sube un PDF desde `/uploads`.
2. Next.js envia el archivo a `POST /api/v1/files/upload`.
3. El backend guarda el PDF en `UPLOAD_DIR`.
4. `ParserFactory` extrae texto y detecta banco/tipo:
   - `BBVA` + `VISA PLATINUM`: `BBVAVisaParser`.
   - `Banco Nacion`/`BNA` + `VISA SIGNATURE`: `BNAVisaParser`.
   - Si no reconoce: `GenericVisaParser`.
5. El parser extrae movimientos y resumen.
6. El clasificador por reglas asigna categoria y tipo de gasto.
7. Se persisten `uploaded_files`, `statement_summaries` y `transactions`.
8. La importacion evita duplicados por usuario, fecha, descripcion, importe, banco y tipo de tarjeta.
9. El backend ejecuta el analisis IA con OpenAI si `OPENAI_API_KEY` esta configurada.
10. Se persiste el resultado en `pdf_ai_analyses`.
11. El frontend muestra los movimientos extraidos y el analisis IA.

El backend registra eventos de diagnostico:

- `pdf_upload_started`
- `pdf_parser_detected`
- `pdf_parsed`
- `pdf_upload_completed`
- `pdf_upload_failed`

La respuesta de `POST /api/v1/files/upload` incluye metricas de procesamiento: parser, banco, movimientos extraidos, movimientos nuevos y duplicados. `GET /api/v1/files` devuelve el historial de archivos del usuario.

Cuando la IA esta habilitada, la misma respuesta incluye `ai_analysis` con estado, modelo, resumen, insights, sugerencias de categoria y anomalias. Si falta `OPENAI_API_KEY` o el PDF no tiene movimientos, el registro queda en estado `skipped`.

## Parsers

La clase base centraliza:

- Extraccion de texto con `pdfplumber`.
- Fallback con `PyMuPDF`.
- Normalizacion de lineas.
- Interpretacion de importes argentinos:
  - `1.102.843,98` -> `1102843.98`
  - `3.546,20-` -> `-3546.20`
- Deteccion de cuotas:
  - `Cuota 06/06`
  - `Cuota 21/24`
- Exclusion de saldos, pagos, vencimientos y totales.

Los parsers especificos heredan de `BaseParser` y fijan metadatos de banco/tarjeta.

## Clasificacion

El MVP usa reglas deterministicas en `app/services/classifier.py`.

Ejemplos:

- `DIA`, `CARREFOUR`, `EXPRESS AMENABAR` -> Supermercado.
- `PEDIDOSYA` -> Delivery.
- `OSDE` -> Salud, fijo.
- `NACION SEGUROS`, `LIFE SEGUROS` -> Seguros, fijo.
- `DB IVA` -> Impuestos.
- `COMISION MANT` -> Servicios bancarios.
- Cuotas detectadas -> gasto fijo.

La tabla `classification_rules` queda preparada para reglas por usuario.

## IA con OpenAI

`app/ai/classifier.py` contiene `AIClassifier`, que usa el SDK oficial de OpenAI.

La IA no recibe el binario del PDF. Recibe un JSON normalizado con:

- Banco y tipo de tarjeta.
- Saldos detectados por el parser.
- Categorias disponibles del sistema.
- Movimientos extraidos y clasificados por reglas.

El objetivo de esta capa es explicar el resumen y detectar oportunidades:

- Resumen financiero del PDF.
- Insights accionables.
- Sugerencias de categoria y tipo de gasto.
- Anomalias o movimientos que merecen revision.

La salida se exige como JSON estructurado y se guarda en `pdf_ai_analyses`. El modelo se configura con `OPENAI_MODEL`, por defecto `gpt-4o-mini`.

## Dashboard e insights

`GET /api/v1/dashboard/summary` consolida:

- Ingresos manuales.
- Gastos importados desde tarjetas.
- Gastos manuales.

Devuelve:

- Ingresos.
- Gastos.
- Ahorro.
- Porcentaje de ahorro.
- Gastos por categoria.
- Evolucion mensual.
- Fijos vs variables.
- Top gastos.
- Comercios frecuentes.
- Gastos hormiga.

`GET /api/v1/insights` detecta:

- Ahorro mensual bajo o saludable.
- Carga fija alta respecto de ingresos.
- Presupuestos al 80% o excedidos.
- Gastos hormiga por comercios repetidos.

## Consultas

`GET /api/v1/reports/cashflow` entrega una vista unificada de ingresos y gastos.

Soporta filtros por:

- Agrupacion mensual o anual.
- Tipo de registro: ingresos, gastos o ambos.
- Origen: PDF o carga manual.
- Categoria de gasto.
- Categoria de ingreso.
- Tipo: fijo, variable o excepcional.
- Año, mes, fecha exacta o rango de fechas.
- Texto en descripcion o categoria.

Los gastos importados desde PDFs usan `transactions.transaction_date`, que corresponde a la fecha de consumo extraida del resumen. Los gastos manuales usan `manual_expenses.expense_date` y los ingresos usan `manual_income.income_date`.

La pantalla `/consultas` consume este endpoint y muestra KPIs, graficos por periodo, categorias principales y tabla de detalle.

## Presupuestos

`budgets` define limites mensuales por categoria.

Los presupuestos se comparan contra:

- Movimientos importados en `transactions`.
- Gastos manuales en `manual_expenses`.

## Ingresos

Los ingresos manuales mantienen una logica equivalente a los gastos:

- `manual_income.income_category_id`: FK obligatoria a `income_categories`.
- `manual_income.income_type`: valor controlado `fixed` o `variable`.

Categorias de ingreso del sistema:

- Ingresos Lau
- Sueldo Fede
- Fondo Fede
- PEF Fede
- Comisiones
- Bonos
- Aguinaldo

## Categorias

Existen dos administradores separados en el frontend:

- `/categories`: categorias de gastos.
- `/income-categories`: categorias de ingresos.

Ambos tienen alta, modificacion y baja. La baja es logica mediante `is_active = false` para conservar consistencia historica: movimientos, gastos o ingresos existentes siguen apuntando a su categoria original aunque ya no aparezca como opcion activa para nuevas cargas.

## Modelo de datos

Tablas principales:

- `users`
- `accounts`
- `cards`
- `categories`
- `transactions`
- `manual_expenses`
- `manual_income`
- `income_categories`
- `uploaded_files`
- `statement_summaries`
- `pdf_ai_analyses`
- `classification_rules`
- `budgets`

`transactions` conserva datos crudos y normalizados para permitir auditoria y reclasificacion sin perder el texto original del resumen.

## Deploy

Railway usa servicios separados:

- Backend: root `backend`, Dockerfile Python.
- Frontend: root `frontend`, Dockerfile Node/Next.js.
- MySQL: servicio Railway independiente.

Variables clave:

- Backend: `MYSQL_URL`, `SECRET_KEY`, `UPLOAD_DIR`, `OPENAI_API_KEY`, `OPENAI_MODEL`.
- Frontend: `NEXT_PUBLIC_API_URL`.

## Escalabilidad

Proximos pasos recomendados:

- Jobs asincronicos para PDFs grandes.
- Almacenamiento externo de PDFs.
- Auditoria de cambios.
- Reglas aprendidas por usuario.
- CRUD completo para ingresos, gastos, categorias y movimientos.
- Tests con fixtures anonimizados de PDFs reales.
