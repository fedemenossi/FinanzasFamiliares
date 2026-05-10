import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import fitz
import pdfplumber


@dataclass
class ParsedTransaction:
    transaction_date: datetime
    raw_description: str
    amount: Decimal
    currency: str = "ARS"
    voucher_number: str | None = None
    cardholder_name: str | None = None
    card_last_digits: str | None = None
    is_installment: bool = False
    installment_current: int | None = None
    installment_total: int | None = None


@dataclass
class ParsedStatement:
    bank_name: str
    card_brand: str | None = None
    card_type: str | None = None
    transactions: list[ParsedTransaction] = field(default_factory=list)
    previous_balance: Decimal | None = None
    current_balance: Decimal | None = None
    minimum_payment: Decimal | None = None
    raw_text: str = ""
    diagnostic_lines: list[str] = field(default_factory=list)
    candidate_lines: list[str] = field(default_factory=list)


class BaseParser:
    bank_name = "Desconocido"
    card_brand = "Visa"
    card_type = None

    skip_keywords = (
        "SALDO ANTERIOR",
        "SALDO ACTUAL",
        "PAGO MINIMO",
        "PAGO MÍNIMO",
        "TOTAL",
        "VENCIMIENTO",
        "LIMITE",
        "LÍMITE",
        "SU PAGO",
        "PAGO RECIBIDO",
    )

    def parse(self, pdf_path: str | Path) -> ParsedStatement:
        text = self.extract_text(pdf_path)
        statement = ParsedStatement(
            bank_name=self.bank_name,
            card_brand=self.card_brand,
            card_type=self.card_type,
            raw_text=text,
        )
        statement.transactions = self.extract_transactions(text)
        statement.diagnostic_lines = self.get_diagnostic_lines(text)
        statement.candidate_lines = self.get_candidate_lines(text)
        statement.previous_balance = self.find_labeled_amount(text, ("SALDO ANTERIOR",))
        statement.current_balance = self.find_labeled_amount(text, ("SALDO ACTUAL", "SALDO AL CIERRE"))
        statement.minimum_payment = self.find_labeled_amount(text, ("PAGO MINIMO", "PAGO MÍNIMO"))
        return statement

    def extract_text(self, pdf_path: str | Path) -> str:
        parts: list[str] = []
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
                    if text.strip():
                        parts.append(text)
        except Exception:
            parts = []

        if parts:
            return "\n".join(parts)

        doc = fitz.open(str(pdf_path))
        try:
            return "\n".join(page.get_text("text") for page in doc)
        finally:
            doc.close()

    def extract_transactions(self, text: str) -> list[ParsedTransaction]:
        transactions: list[ParsedTransaction] = []
        for line in text.splitlines():
            parsed = self.parse_transaction_line(line)
            if parsed:
                transactions.append(parsed)
        return transactions

    def parse_transaction_line(self, line: str) -> ParsedTransaction | None:
        cleaned = " ".join(line.strip().split())
        if not cleaned or self.should_skip(cleaned):
            return None

        date_match = re.match(r"^(?P<date>\d{2}[\/\-.]\d{2}(?:[\/\-.]\d{2,4})?)\s+(?P<body>.+)$", cleaned)
        if not date_match:
            return None

        amount_matches = list(
            re.finditer(
                r"(?P<amount>-?(?:\$|ARS|U\$S|USD)?\s*\d{1,3}(?:\.\d{3})*,\d{2}-?|-?(?:\$|ARS|U\$S|USD)?\s*\d{4,},\d{2}-?)",
                cleaned,
                flags=re.IGNORECASE,
            )
        )
        if not amount_matches:
            return None

        amount_match = amount_matches[-1]
        body = date_match.group("body").strip()
        description = cleaned[date_match.end("date") : amount_match.start()].strip()
        description = re.sub(r"^(?:\d{2}[\/\-.]\d{2}(?:[\/\-.]\d{2,4})?)\s+", "", description)
        voucher_match = re.match(r"^(?P<voucher>\d{4,}[A-Z*]?)\s+(?P<desc>.+)$", description)
        voucher = None
        if voucher_match:
            voucher = voucher_match.group("voucher")
            description = voucher_match.group("desc").strip()

        description = self.clean_description(description)

        if not description or self.should_skip(description):
            return None

        current, total = self.detect_installment(description)
        return ParsedTransaction(
            transaction_date=self.parse_date(date_match.group("date")),
            voucher_number=voucher,
            raw_description=description,
            amount=parse_argentine_amount(amount_match.group("amount")),
            is_installment=current is not None,
            installment_current=current,
            installment_total=total,
        )

    def should_skip(self, value: str) -> bool:
        upper = value.upper()
        return any(keyword in upper for keyword in self.skip_keywords)

    def parse_date(self, value: str) -> datetime:
        parts = re.split(r"[\/\-.]", value)
        day, month = int(parts[0]), int(parts[1])
        if len(parts) == 3:
            year = int(parts[2])
            if year < 100:
                year += 2000
        else:
            year = datetime.utcnow().year
        return datetime(year, month, day)

    def detect_installment(self, description: str) -> tuple[int | None, int | None]:
        match = re.search(r"(?:CUOTA|C\.?)\s*(\d{1,2})\s*/\s*(\d{1,2})", description, re.IGNORECASE)
        if not match:
            return None, None
        return int(match.group(1)), int(match.group(2))

    def clean_description(self, description: str) -> str:
        value = " ".join(description.strip().split())
        value = re.sub(r"\s+(?:\$|ARS|U\$S|USD)?\s*\d{1,3}(?:\.\d{3})*,\d{2}-?$", "", value, flags=re.IGNORECASE)
        value = re.sub(r"\b\d{8,}\b(?:\s*-\d{3}){0,3}\b", "", value)
        value = re.sub(r"\b\d{3,}-\d{3,}-\d{3,}\b", "", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip(" -")

    def find_labeled_amount(self, text: str, labels: tuple[str, ...]) -> Decimal | None:
        for line in text.splitlines():
            upper = line.upper()
            if any(label in upper for label in labels):
                amounts = re.findall(r"-?\$?\s*\d{1,3}(?:\.\d{3})*,\d{2}-?", line)
                if amounts:
                    return parse_argentine_amount(amounts[-1])
        return None

    def get_candidate_lines(self, text: str, limit: int = 40) -> list[str]:
        candidates: list[str] = []
        for line in text.splitlines():
            cleaned = " ".join(line.strip().split())
            if not cleaned or self.should_skip(cleaned):
                continue
            has_date = re.search(r"\d{2}[\/\-.]\d{2}(?:[\/\-.]\d{2,4})?", cleaned)
            has_amount = re.search(r"\d{1,3}(?:\.\d{3})*,\d{2}|\d{4,},\d{2}", cleaned)
            if has_date and has_amount:
                candidates.append(cleaned[:500])
            if len(candidates) >= limit:
                break
        return candidates

    def get_diagnostic_lines(self, text: str, limit: int = 25) -> list[str]:
        lines: list[str] = []
        for line in text.splitlines():
            cleaned = " ".join(line.strip().split())
            if cleaned:
                lines.append(cleaned[:500])
            if len(lines) >= limit:
                break
        return lines


def parse_argentine_amount(value: str) -> Decimal:
    raw = value.strip().replace("$", "").replace(" ", "")
    negative = raw.endswith("-") or raw.startswith("-")
    raw = raw.strip("-").replace(".", "").replace(",", ".")
    amount = Decimal(raw)
    return -amount if negative else amount


def normalize_description(description: str) -> str:
    value = re.sub(r"\s+", " ", description.upper()).strip()
    value = re.sub(r"\bCUOTA\s+\d{1,2}/\d{1,2}\b", "", value, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", value).strip()
