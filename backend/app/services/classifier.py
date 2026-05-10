from dataclasses import dataclass


SYSTEM_CATEGORIES = [
    ("Supermercado", "#2E7D32"),
    ("Delivery", "#EF6C00"),
    ("Salud", "#C62828"),
    ("Seguros", "#1565C0"),
    ("Impuestos", "#6A1B9A"),
    ("Streaming", "#00838F"),
    ("Clubes", "#455A64"),
    ("Restaurantes", "#AD1457"),
    ("Cafeterías", "#795548"),
    ("Entretenimiento", "#5E35B1"),
    ("Viajes", "#0277BD"),
    ("Compras", "#6D4C41"),
    ("Hogar", "#558B2F"),
    ("Servicios", "#37474F"),
    ("Servicios bancarios", "#263238"),
    ("Educación", "#283593"),
    ("Transporte", "#00695C"),
    ("Otros", "#607D8B"),
]


@dataclass(frozen=True)
class Classification:
    category_name: str
    expense_type: str


RULES: list[tuple[str, Classification]] = [
    ("DIA", Classification("Supermercado", "variable")),
    ("CARREFOUR", Classification("Supermercado", "variable")),
    ("EXPRESS AMENABAR", Classification("Supermercado", "variable")),
    ("PEDIDOSYA", Classification("Delivery", "variable")),
    ("DLO*PEDIDOSYA", Classification("Delivery", "variable")),
    ("OSDE", Classification("Salud", "fixed")),
    ("NACION SEGUROS", Classification("Seguros", "fixed")),
    ("LIFE SEGUROS", Classification("Seguros", "fixed")),
    ("SEGUROS", Classification("Seguros", "fixed")),
    ("DB IVA", Classification("Impuestos", "fixed")),
    ("IVA", Classification("Impuestos", "fixed")),
    ("PLATEANET", Classification("Entretenimiento", "variable")),
    ("LOLA MEMBRIVES", Classification("Entretenimiento", "variable")),
    ("ARANCELES SOCIOS", Classification("Clubes", "fixed")),
    ("CUOTA SOCIAL CAR", Classification("Clubes", "fixed")),
    ("COMISION MANT", Classification("Servicios bancarios", "fixed")),
    ("COMISION", Classification("Servicios bancarios", "fixed")),
    ("BNA VIAJES", Classification("Viajes", "fixed")),
    ("MEGATONE", Classification("Compras", "fixed")),
    ("METROTEL", Classification("Servicios", "fixed")),
    ("TICKETING", Classification("Entretenimiento", "variable")),
    ("ASOCIACION DE ME", Classification("Salud", "fixed")),
    ("SOC DE OBSTETRIC", Classification("Salud", "fixed")),
    ("NETFLIX", Classification("Streaming", "fixed")),
    ("SPOTIFY", Classification("Streaming", "fixed")),
]


def classify(description: str, is_installment: bool = False) -> Classification:
    upper = description.upper()
    for pattern, classification in RULES:
        if pattern in upper:
            if is_installment and classification.expense_type == "variable":
                return Classification(classification.category_name, "fixed")
            return classification
    if is_installment:
        return Classification("Compras", "fixed")
    return Classification("Otros", "variable")
