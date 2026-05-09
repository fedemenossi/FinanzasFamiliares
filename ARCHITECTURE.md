# Arquitectura

## Visión general

El sistema está dividido en tres capas:

- Backend FastAPI: API REST, autenticación, persistencia, procesamiento de PDFs y clasificación.
- MySQL 8: datos transaccionales, usuarios, categorías, movimientos y archivos.
- Frontend Streamlit: experiencia de usuario para carga, edición y análisis financiero.

## Backend

Módulos principales:

- `app/api`: routers HTTP.
- `app/models`: modelos SQLAlchemy 2.x.
- `app/schemas`: contratos Pydantic.
- `app/parsers`: arquitectura extensible de parsers bancarios.
- `app/services`: reglas de clasificación y bootstrap de categorías.
- `app/ai`: punto de extensión para clasificación con OpenAI.

## Flujo de PDFs

1. El usuario sube un PDF en Streamlit.
2. Streamlit envía el archivo a `POST /api/v1/files/upload`.
3. El backend guarda el PDF en `UPLOAD_DIR`.
4. `ParserFactory` extrae texto y detecta banco/tipo:
   - `BBVA` + `VISA PLATINUM`: `BBVAVisaParser`.
   - `Banco Nación`/`Banco Nacion`/`BNA` + `VISA SIGNATURE`: `BNAVisaParser`.
   - Si no reconoce: `GenericVisaParser`.
5. El parser extrae movimientos y resumen.
6. El clasificador por reglas asigna categoría y tipo de gasto.
7. Se persisten `uploaded_files`, `statement_summaries` y `transactions`.

## Parsers

La clase base centraliza:

- Extracción de texto con `pdfplumber`.
- Fallback con `PyMuPDF`.
- Normalización de líneas.
- Interpretación de importes argentinos:
  - `1.102.843,98` -> `1102843.98`
  - `3.546,20-` -> `-3546.20`
- Detección de cuotas:
  - `Cuota 06/06`
  - `Cuota 21/24`
- Exclusión de saldos, pagos, vencimientos y totales.

Los parsers específicos heredan de `BaseParser` y fijan metadatos de banco/tarjeta. En una evolución posterior se pueden sobreescribir patrones por banco cuando aparezcan variaciones reales de layout.

## Clasificación

El MVP usa reglas determinísticas en `app/services/classifier.py`.

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
- Gastos por categoría.
- Evolución mensual.
- Fijos vs variables.
- Top gastos.
- Comercios frecuentes.
- Gastos hormiga.

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

`transactions` conserva datos crudos y normalizados para permitir auditoría y reclasificación sin perder el texto original del resumen.

## IA futura

`app/ai/classifier.py` define un placeholder para integrar OpenAI, por ejemplo con GPT-4o-mini. La intención es usar IA como segunda capa:

1. Reglas exactas para comercios conocidos.
2. Reglas del usuario.
3. IA para comercios ambiguos.
4. Confirmación o corrección manual para mejorar reglas futuras.

## Escalabilidad

La separación parser/factory/clasificador permite sumar bancos sin modificar endpoints. La autenticación ya usa `user_id` en todas las entidades críticas, por lo que el modelo está preparado para multiusuario. Para SaaS real convendría sumar:

- Jobs asincrónicos para PDFs grandes.
- Almacenamiento externo de PDFs.
- Deduplicación de movimientos.
- Auditoría de cambios.
- Reglas aprendidas por usuario.
- Tests con fixtures anonimizados de PDFs reales.
