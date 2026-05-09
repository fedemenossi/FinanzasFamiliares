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

        match = re.match(
            r"^(?P<date>\d{2}[/-]\d{2}(?:[/-]\d{2,4})?)\s+(?:(?P<voucher>\d{4,})\s+)?(?P<desc>.+?)\s+(?P<amount>-?\$?\s*\d{1,3}(?:\.\d{3})*,\d{2}-?)$",
            cleaned,
        )
        if not match:
            return None

        description = match.group("desc").strip()
        if self.should_skip(description):
            return None

        current, total = self.detect_installment(description)
        return ParsedTransaction(
            transaction_date=self.parse_date(match.group("date")),
            voucher_number=match.group("voucher"),
            raw_description=description,
            amount=parse_argentine_amount(match.group("amount")),
            is_installment=current is not None,
            installment_current=current,
            installment_total=total,
        )

    def should_skip(self, value: str) -> bool:
        upper = value.upper()
        return any(keyword in upper for keyword in self.skip_keywords)

    def parse_date(self, value: str) -> datetime:
        parts = re.split(r"[/-]", value)
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

    def find_labeled_amount(self, text: str, labels: tuple[str, ...]) -> Decimal | None:
        for line in text.splitlines():
            upper = line.upper()
            if any(label in upper for label in labels):
                amounts = re.findall(r"-?\$?\s*\d{1,3}(?:\.\d{3})*,\d{2}-?", line)
                if amounts:
                    return parse_argentine_amount(amounts[-1])
        return None


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
