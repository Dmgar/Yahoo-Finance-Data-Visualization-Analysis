"""Utilidades compartidas por los módulos de análisis, proyección y visualización."""

import logging
from collections.abc import Callable, Iterable
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def require_columns(
    df: pd.DataFrame,
    columns: Iterable[str],
    context: str,
    hint: str = "",
    error_type: type[Exception] = ValueError,
) -> None:
    """Verifica que `df` tenga todas las `columns`, o lanza `error_type`."""
    missing = [col for col in columns if col not in df.columns]
    if missing:
        message = f"{context} no incluye las columnas {missing}."
        raise error_type(f"{message} {hint}".strip())


def require_close_prices(df: pd.DataFrame, pair: str) -> pd.DataFrame:
    """Devuelve las filas con precio de cierre; lanza ValueError si no hay ninguna.

    Se limpia solo la columna `Close` para que los NaN iniciales de los
    indicadores rolling no vacíen el DataFrame.
    """
    prices = df.dropna(subset=["Close"])
    if prices.empty:
        raise ValueError(f"El reporte de {pair} no tiene precios de cierre válidos.")
    return prices


def format_metric(value, fmt: str = ".5f", na: str = "N/A") -> str:
    """Formatea una métrica devolviendo `na` cuando es None o NaN."""
    if value is None or pd.isna(value):
        return na
    try:
        return f"{value:{fmt}}"
    except (ValueError, TypeError):
        logger.debug(f"Valor no formateable con '{fmt}': {value!r}", exc_info=True)
        return str(value)


def round_or_none(value, digits: int) -> float | None:
    """Redondea un valor numérico, o devuelve None si es None o NaN."""
    if value is None or pd.isna(value):
        return None
    return round(float(value), digits)


def save_output(path: str, writer: Callable[[str], None], description: str) -> Path:
    """Crea el directorio destino, escribe la salida y avisa por consola.

    `description` ya debe estar conjugada, ej: "Comparación guardada".
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    writer(str(target))
    print(f" {description} en: {target}")
    return target
