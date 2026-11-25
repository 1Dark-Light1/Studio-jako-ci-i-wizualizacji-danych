"""Budowanie wykresów jako obiekty Matplotlib Figure."""

import pandas as pd
from matplotlib.figure import Figure

from .data_session import DataSession


def _numeric_values(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        raise ValueError(f"Nie znaleziono kolumny '{column}'.")
    values = pd.to_numeric(frame[column], errors="coerce").dropna()
    if values.empty:
        raise ValueError("Wybrana kolumna nie zawiera danych liczbowych.")
    return values


def histogram_figure(session: DataSession, column: str) -> Figure:
    values = _numeric_values(session.current, column)
    fig = Figure(figsize=(7, 4), dpi=100)
    axis = fig.add_subplot()
    axis.hist(values, bins="auto", edgecolor="white")
    axis.set_title(f"Rozkład kolumny: {column}")
    axis.set_xlabel(column)
    axis.set_ylabel("Liczba rekordów")
    fig.tight_layout()
    return fig


def scatter_figure(session: DataSession, x_column: str, y_column: str) -> Figure:
    x_values = pd.to_numeric(session.current[x_column], errors="coerce")
    y_values = pd.to_numeric(session.current[y_column], errors="coerce")
    valid = x_values.notna() & y_values.notna()
    if int(valid.sum()) < 2:
        raise ValueError("Scatter wymaga co najmniej dwóch poprawnych par liczbowych.")
    fig = Figure(figsize=(7, 4), dpi=100)
    axis = fig.add_subplot()
    axis.scatter(x_values[valid], y_values[valid], alpha=0.7)
    axis.set_title(f"Zależność: {y_column} od {x_column}")
    axis.set_xlabel(x_column)
    axis.set_ylabel(y_column)
    fig.tight_layout()
    return fig


def box_figure(session: DataSession, column: str) -> Figure:
    values = _numeric_values(session.current, column)
    fig = Figure(figsize=(7, 4), dpi=100)
    axis = fig.add_subplot()
    axis.boxplot(values, orientation="vertical", patch_artist=True)
    axis.set_title(f"Rozkład kwartylowy: {column}")
    axis.set_xlabel(column)
    axis.set_ylabel("Wartość")
    fig.tight_layout()
    return fig


def bar_figure(session: DataSession, column: str) -> Figure:
    if column not in session.current.columns:
        raise ValueError(f"Nie znaleziono kolumny '{column}'.")
    counts = session.current[column].fillna("(brak)").astype(str).value_counts().head(15)
    if counts.empty:
        raise ValueError("Wybrana kolumna nie zawiera danych.")
    fig = Figure(figsize=(7, 4), dpi=100)
    axis = fig.add_subplot()
    axis.bar(counts.index.astype(str), counts.values)
    axis.tick_params(axis="x", rotation=45)
    axis.set_title(f"Liczność kategorii: {column}")
    axis.set_xlabel(column)
    axis.set_ylabel("Liczba rekordów")
    fig.tight_layout()
    return fig


def correlation(session: DataSession) -> tuple[pd.DataFrame, str]:
    numeric = session.current.select_dtypes(include="number")
    if numeric.shape[1] < 2:
        raise ValueError("Analiza korelacji wymaga co najmniej dwóch kolumn liczbowych.")
    table = numeric.corr(numeric_only=True).round(3)
    strongest = ""
    max_value = -1.0
    for i, left in enumerate(table.columns):
        for right in table.columns[i + 1:]:
            value = abs(float(table.loc[left, right]))
            if value > max_value:
                max_value = value
                strongest = f"{left} i {right}: r={table.loc[left, right]:.3f}"
    if not strongest:
        strongest = "Brak par do porównania."
    return table, (
        "Korelacja opisuje relację liniową. Nie oznacza przyczynowości. "
        f"Najjaśniejsza para: {strongest}."
    )