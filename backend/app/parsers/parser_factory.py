from pathlib import Path

from app.parsers.base_parser import BaseParser
from app.parsers.bbva.parser_bbva_visa import BBVAVisaParser
from app.parsers.bna.parser_bna_visa import BNAVisaParser
from app.parsers.generic.parser_generic_visa import GenericVisaParser


class ParserFactory:
    @staticmethod
    def detect_parser(text: str) -> BaseParser:
        upper = text.upper()
        if "BBVA" in upper and "VISA PLATINUM" in upper:
            return BBVAVisaParser()
        if ("BANCO NACIÓN" in upper or "BANCO NACION" in upper or "BNA" in upper) and "VISA SIGNATURE" in upper:
            return BNAVisaParser()
        return GenericVisaParser()

    @staticmethod
    def for_file(pdf_path: str | Path) -> BaseParser:
        generic = GenericVisaParser()
        text = generic.extract_text(pdf_path)
        return ParserFactory.detect_parser(text)
