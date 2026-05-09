# Arquitectura

## Vision general

El sistema esta dividido en tres capas:

- Backend FastAPI: API REST, autenticacion, persistencia, procesamiento de PDFs y clasificacion.
- MySQL 8: datos transaccionales, usuarios, categorias, movimientos y archivos.
- Frontend Streamlit: experiencia de usuario para carga, edicion y analisis financiero.

## Backend

Modulos principales:

- `app/api`: routers HTTP.
- `app/models`: modelos SQLAlchemy 2.x.
- `app/schemas`: contratos Pydantic.
- `app/parsers`: arquitectura extensible de parsers bancarios.
- `app/services`: reglas de clasificacion y bootstrap de categorias.
- `app/ai`: punto de extension para clasificacion con OpenAI.

## Flujo de PDFs

1. El usuario sube un PDF en Streamlit.
2. Streamlit envia el archivo a `POST /api/v1/files/upload`.
3. El backend guarda el PDF en `UPLOAD_DIR`.
4. `ParserFactory` extrae texto y detecta banco/tipo:
   - `BBVA` + `VISA PLATINUM`: `BBVAVisaParser`.
   - `Banco Nacion`/`BNA` + `VISA SIGNATURE`: `BNAVisaParser`.
   - Si no reconoce: `GenericVisaParser`.
5. El parser extrae movimientos y resumen.
6. El clasificador por reglas asigna categoria y tipo de gasto.
7. Se persisten `uploaded_files`, `statement_summaries` y `transactions`.
8. En Fase 2, la importacion evita duplicados por usuario, fecha, descripcion, importe, banco y tipo de tarjeta.

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

Los parsers especificos heredan de `BaseParser` y fijan metadatos de banco/tarjeta. En una evolucion posterior se pueden sobreescribir patrones por banco cuando aparezcan variaciones reales de layout.

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

Esto permite resultados auditables y editables. La tabla `classification_rules` queda preparada para reglas por usuario.

## Dashboard

`GET /api/v1/dashboard/summary` consolida:

- Ingresos manuales.
- Gastos importados desde tarjetas.
- Gastos manuales.

Devuelve KPIs y series listas para graficar:

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

## Fase 2: presupuestos e insights

La Fase 2 incorpora una capa de control:

- `budgets`: define limites mensuales por categoria.
- `insights`: interpreta gastos, ingresos y presupuestos para generar alertas.
- Deduplicacion de importaciones: evita duplicar movimientos cuando se sube dos veces un mismo resumen o resumen solapado.

Los presupuestos se comparan contra:

- Movimientos importados en `transactions`.
- Gastos manuales en `manual_expenses`.

Los insights actuales detectan:

- Ahorro mensual bajo o saludable.
- Carga fija alta respecto de ingresos.
- Presupuestos al 80% o excedidos.
- Gastos hormiga por comercios repetidos.

## Modelo de datos

Tablas principales:

- `users`
- `accounts`
- `cards`
- `categories`
- `transactions`
- `manual_expenses`
- `manual_income`
- `uploaded_files`
- `statement_summaries`
- `classification_rules`
- `budgets`

`transactions` conserva datos crudos y normalizados para permitir auditoria y reclasificacion sin perder el texto original del resumen.

## IA futura

`app/ai/classifier.py` define un placeholder para integrar OpenAI, por ejemplo con GPT-4o-mini. La intencion es usar IA como segunda capa:

1. Reglas exactas para comercios conocidos.
2. Reglas del usuario.
3. IA para comercios ambiguos.
4. Confirmacion o correccion manual para mejorar reglas futuras.

## Escalabilidad

La separacion parser/factory/clasificador permite sumar bancos sin modificar endpoints. La autenticacion ya usa `user_id` en todas las entidades criticas, por lo que el modelo esta preparado para multiusuario. Para SaaS real convendria sumar:

- Jobs asincronicos para PDFs grandes.
- Almacenamiento externo de PDFs.
- Auditoria de cambios.
- Reglas aprendidas por usuario.
- Tests con fixtures anonimizados de PDFs reales.
