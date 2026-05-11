import json
import logging
from decimal import Decimal
from typing import Any

from openai import OpenAI

from app.core.config import get_settings
from app.parsers.base_parser import ParsedStatement
from app.services.classifier import SYSTEM_CATEGORIES


logger = logging.getLogger(__name__)


AI_ANALYSIS_SCHEMA: dict[str, Any] = {
    "name": "pdf_financial_analysis",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "summary": {"type": "string"},
            "insights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "detail": {"type": "string"},
                        "severity": {"type": "string", "enum": ["info", "warning", "critical"]},
                    },
                    "required": ["title", "detail", "severity"],
                },
            },
            "category_suggestions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "description": {"type": "string"},
                        "suggested_category": {"type": "string"},
                        "expense_type": {"type": "string", "enum": ["fixed", "variable", "exceptional"]},
                        "confidence": {"type": "number"},
                        "reason": {"type": "string"},
                    },
                    "required": ["description", "suggested_category", "expense_type", "confidence", "reason"],
                },
            },
            "anomalies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "description": {"type": "string"},
                        "amount": {"type": "number"},
                        "reason": {"type": "string"},
                    },
                    "required": ["description", "amount", "reason"],
                },
            },
        },
        "required": ["summary", "insights", "category_suggestions", "anomalies"],
    },
    "strict": True,
}


class AIClassifier:
    """Analiza movimientos extraidos de un PDF con OpenAI.

    No reemplaza los parsers ni las reglas deterministicas. Opera como capa
    posterior para explicar el resumen y sugerir mejoras de clasificacion.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.openai_api_key)

    def analyze_statement(self, statement: ParsedStatement, classified_transactions: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not self.enabled:
            logger.info("openai_analysis_skipped reason=missing_api_key")
            return None

        payload = {
            "bank_name": statement.bank_name,
            "card_brand": statement.card_brand,
            "card_type": statement.card_type,
            "previous_balance": decimal_to_float(statement.previous_balance),
            "current_balance": decimal_to_float(statement.current_balance),
            "minimum_payment": decimal_to_float(statement.minimum_payment),
            "available_categories": [name for name, _ in SYSTEM_CATEGORIES],
            "transactions": classified_transactions[:120],
        }

        client = OpenAI(api_key=self.settings.openai_api_key)
        logger.info(
            "openai_analysis_started model=%s bank=%s transactions=%s",
            self.settings.openai_model,
            statement.bank_name,
            len(classified_transactions),
        )
        response = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sos un analista financiero familiar especializado en Argentina. "
                        "Analiza resumenes de tarjeta ya parseados. No inventes datos. "
                        "Usa tono claro, accionable y conservador. "
                        "Las categorias sugeridas deben pertenecer a available_categories."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
            response_format={"type": "json_schema", "json_schema": AI_ANALYSIS_SCHEMA},
            temperature=0.2,
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        logger.info("openai_analysis_completed model=%s", self.settings.openai_model)
        return parsed


def decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)
