"""Perfilamiento y tratamiento conservador del conjunto de datos del proyecto.

No reemplaza el archivo fuente: las correcciones se generan en memoria para que
el diagnóstico sea reproducible y la fuente permanezca trazable.
"""

from __future__ import annotations

import csv
import datetime as dt
import io
import math
from collections import Counter
from pathlib import Path


DATASET = Path(__file__).parent / "data" / "processed" / "dataset_consolidado_r1.csv"
NUMERIC_COLUMNS = ("Patrimonio_Total", "Activo_Total", "Pasivo_Total", "Razon_Endeudamiento")
FINANCIAL_COLUMNS = ("Patrimonio_Total", "Activo_Total", "Pasivo_Total")
DOMAINS = {
    "Tamano_Empresa": {"Micro", "Pequeña", "Mediana", "Grande"},
    "Insolvencia_Tecnica": {"Sí", "No"},
    "Pais_Matriz": {"COL"},
}


def _percent(value: int | float, total: int | float) -> float:
    return round(100 * value / total, 2) if total else 0.0


def _read_rows():
    with DATASET.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        return reader.fieldnames, list(reader)


def _outlier_count(values: list[float]) -> int:
    """Cuenta atípicos mediante el rango intercuartílico (IQR)."""
    if len(values) < 4:
        return 0
    ordered = sorted(values)
    q1 = ordered[round((len(ordered) - 1) * .25)]
    q3 = ordered[round((len(ordered) - 1) * .75)]
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return sum(value < lower or value > upper for value in values)


def build_report():
    columns, rows = _read_rows()
    record_count = len(rows)
    profiles = []
    null_counts = {}

    for column in columns:
        raw = [row[column].strip() for row in rows]
        present = [value for value in raw if value]
        null_counts[column] = record_count - len(present)
        profile = {
            "name": column,
            "type": "numérico" if column in NUMERIC_COLUMNS or column == "Ano_Corte" else "texto/fecha",
            "unique": len(set(present)),
            "nulls": null_counts[column],
            "null_percent": _percent(null_counts[column], record_count),
            "minimum": "—", "maximum": "—", "average": "—", "outliers": "—",
        }
        if column in NUMERIC_COLUMNS or column == "Ano_Corte":
            values = [float(value) for value in present if math.isfinite(float(value))]
            if values:
                profile.update({
                    "minimum": f"{min(values):,.2f}", "maximum": f"{max(values):,.2f}",
                    "average": f"{sum(values) / len(values):,.2f}",
                    "outliers": _outlier_count(values) if column in FINANCIAL_COLUMNS else "—",
                })
        profiles.append(profile)

    exact_duplicates = record_count - len({tuple(row[column] for column in columns) for row in rows})
    key_duplicates = record_count - len({(row["nit"], row["fecha_corte"]) for row in rows})
    ratio_infinite = sum(row["Razon_Endeudamiento"] in {"inf", "-inf"} for row in rows)
    date_year_errors = 0
    balance_rows = balance_valid = 0
    unexpected_dates = 0
    for row in rows:
        try:
            date = dt.date.fromisoformat(row["fecha_corte"])
            if date.year != int(row["Ano_Corte"]):
                date_year_errors += 1
            if date.month != 12 or date.day != 31:
                unexpected_dates += 1
        except (TypeError, ValueError):
            date_year_errors += 1
        if all(row[column].strip() for column in FINANCIAL_COLUMNS):
            balance_rows += 1
            assets = float(row["Activo_Total"])
            liabilities = float(row["Pasivo_Total"])
            equity = float(row["Patrimonio_Total"])
            if abs(assets - liabilities - equity) <= max(1, abs(assets) * .01):
                balance_valid += 1

    valid_ratio = sum(
        bool(row["Razon_Endeudamiento"]) and math.isfinite(float(row["Razon_Endeudamiento"]))
        for row in rows
    )
    ratio_present = record_count - null_counts["Razon_Endeudamiento"]
    nonempty_cells = sum(record_count - count for count in null_counts.values())
    recent_records = sum(int(row["Ano_Corte"]) >= 2024 for row in rows)
    measures = [
        {"dimension": "Completitud", "formula": "celdas no vacías / celdas evaluadas", "value": _percent(nonempty_cells, record_count * len(columns)), "detail": f"{nonempty_cells:,} de {record_count * len(columns):,} celdas con valor."},
        {"dimension": "Exactitud (balance)", "formula": "balances que cumplen A = P + Patrimonio / balances completos", "value": _percent(balance_valid, balance_rows), "detail": f"{balance_valid:,} de {balance_rows:,} registros con los tres valores financieros concuerdan (tolerancia 1%)."},
        {"dimension": "Consistencia temporal", "formula": "fecha_corte coherente con Ano_Corte / registros", "value": _percent(record_count - date_year_errors, record_count), "detail": f"{date_year_errors:,} diferencias entre año y fecha."},
        {"dimension": "Unicidad", "formula": "claves nit + fecha_corte no repetidas / registros", "value": _percent(record_count - key_duplicates, record_count), "detail": f"{key_duplicates:,} claves duplicadas; {exact_duplicates:,} filas idénticas."},
        {"dimension": "Validez", "formula": "razones de endeudamiento finitas / razones informadas", "value": _percent(valid_ratio, ratio_present), "detail": f"{ratio_infinite:,} valores infinitos por activo igual a cero."},
        {"dimension": "Actualidad", "formula": "registros de 2024–2025 / registros", "value": _percent(recent_records, record_count), "detail": f"{recent_records:,} registros recientes; el último período disponible es 2025."},
    ]
    problems = [
        {"field": column, "description": "Valores ausentes; se conservarán como 'sin reporte' para no inventar información financiera.", "count": count, "dimension": "Completitud", "impact": "Alto" if _percent(count, record_count) > 50 else "Medio"}
        for column, count in null_counts.items() if count
    ]
    problems.extend([
        {"field": "Razon_Endeudamiento", "description": "Valor infinito: activo total igual a cero y pasivo positivo; la razón no es interpretable.", "count": ratio_infinite, "dimension": "Validez", "impact": "Medio"},
        {"field": "fecha_corte", "description": "Fechas distintas al cierre anual 31 de diciembre; requieren validación contra la fuente.", "count": unexpected_dates, "dimension": "Consistencia", "impact": "Bajo"},
        {"field": "Activo_Total, Pasivo_Total, Patrimonio_Total", "description": "El balance contable no concuerda dentro de una tolerancia de 1% cuando los tres valores están disponibles.", "count": balance_rows - balance_valid, "dimension": "Exactitud", "impact": "Alto"},
    ])
    return {"records": record_count, "variables": len(columns), "profiles": profiles, "measures": measures,
            "problems": [problem for problem in problems if problem["count"]],
            "before": {"infinite_ratio": ratio_infinite, "duplicates": exact_duplicates, "trimmed_text": 0},
            "after": {"infinite_ratio": 0, "duplicates": exact_duplicates, "trimmed_text": 0}}


def treated_csv():
    """Entrega una copia tratada sin alterar el CSV original."""
    columns, rows = _read_rows()
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        cleaned = {column: value.strip() for column, value in row.items()}
        if cleaned["Razon_Endeudamiento"] in {"inf", "-inf"}:
            cleaned["Razon_Endeudamiento"] = ""
        writer.writerow(cleaned)
    return output.getvalue()
