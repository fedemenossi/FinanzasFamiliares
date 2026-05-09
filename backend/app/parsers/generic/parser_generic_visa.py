from app.parsers.base_parser import BaseParser


class GenericVisaParser(BaseParser):
    bank_name = "Banco no reconocido"
    card_brand = "Visa"
    card_type = "Resumen genérico"
