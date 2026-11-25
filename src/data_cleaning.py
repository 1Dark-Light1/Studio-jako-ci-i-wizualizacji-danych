"""Czyste, niezależne od GUI operacje na zbiorze danych."""

from typing import Literal

import pandas as pd


def numeric_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        raise ValueError(f"Nie znaleziono kolumny '{column}'.")
    return pd.to_numeric(frame[column], errors="coerce")


def impute_missing(
    frame: pd.DataFrame,
    column: str,
    strategy: Literal["delete", "mean", "median", "mode", "constant"],
    constant: object = None,
) -> tuple[pd.DataFrame, int]:
    if column not in frame.columns:
        raise ValueError(f"Nie znaleziono kolumny '{column}'.")

    result = frame.copy(deep=True)
    missing = result[column].isna()
    affected = int(missing.sum())
    if affected == 0:
        return result, 0

    if strategy == "delete":
        result = result.loc[~missing].copy()
    elif strategy in {"mean", "median"}:
        values = numeric_series(result, column)
        if not values.notna().any():
            raise ValueError("Kolumna nie ma wartości liczbowych do imputacji.")
        replacement = values.mean() if strategy == "mean" else values.median()
        result[column] = values
        result.loc[missing, column] = replacement
    elif strategy == "mode":
        if not result[column].dropna().empty:
            replacement = result[column].dropna().mode().iloc[0]
            result.loc[missing, column] = replacement
    elif strategy == "constant":
        if constant is None:
            raise ValueError("Podaj stałą wartość.")
        result.loc[missing, column] = constant
    else:
        raise ValueError("Nieznana strategia uzupełniania braków.")

    return result, affected


def convert_numeric_column(frame: pd.DataFrame, column: str) -> tuple[pd.DataFrame, int]:
    if column not in frame.columns:
        raise ValueError(f"Nie znaleziono kolumny '{column}'.")
    result = frame.copy(deep=True)
    converted = numeric_series(result, column)
    changed = int((~converted.isna() & ~pd.to_numeric(
        result[column].astype(str).str.strip(), errors="coerce"
    ).isna()).sum())
    invalid = int((converted.isna() & result[column].notna()).sum())
    result[column] = converted
    return result, invalid


def range_mask(
    frame: pd.DataFrame,
    column: str,
    minimum: float | None,
    maximum: float | None,
) -> pd.Series:
    values = numeric_series(frame, column)
    if minimum is None and maximum is None:
        raise ValueError("Podaj co najmniej dolną albo górną granicę.")
    mask = pd.Series(False, index=frame.index)
    if minimum is not None:
        mask |= values.notna() & (values < minimum)
    if maximum is not None:
        mask |= values.notna() & (values > maximum)
    return mask


def apply_range(
    frame: pd.DataFrame,
    column: str,
    minimum: float | None,
    maximum: float | None,
    action: Literal["mark", "remove", "clamp"],
) -> tuple[pd.DataFrame, int]:
    result = frame.copy(deep=True)
    mask = range_mask(result, column, minimum, maximum)
    affected = int(mask.sum())
    if affected == 0:
        return result, 0

    if action == "mark":
        flag = f"{column}_poza_zakresem"
        result[flag] = False
        result.loc[mask, flag] = True
    elif action == "remove":
        result = result.loc[~mask].copy()
    elif action == "clamp":
        values = numeric_series(result, column)
        if minimum is not None:
            values = values.mask(mask & (values < minimum), minimum)
        if maximum is not None:
            values = values.mask(mask & (values > maximum), maximum)
        result[column] = values
    else:
        raise ValueError("Nieznana akcja dla wartości poza zakresem.")

    return result, affected


def iqr_mask(frame: pd.DataFrame, column: str, factor: float = 1.5) -> pd.Series:
    values = numeric_series(frame, column)
    q1, q3 = values.quantile([0.25, 0.75])
    if pd.isna(q1) or pd.isna(q3):
        return pd.Series(False, index=frame.index)
    iqr = q3 - q1
    if iqr == 0:
        return pd.Series(False, index=frame.index)
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    return values.notna() & ((values < lower) | (values > upper))


def apply_outliers(
    frame: pd.DataFrame,
    column: str,
    factor: float,
    action: Literal["mark", "remove", "clamp"],
) -> tuple[pd.DataFrame, int]:
    if factor <= 0:
        raise ValueError("Współczynnik IQR musi być większy od zera.")
    result = frame.copy(deep=True)
    mask = iqr_mask(result, column, factor)
    affected = int(mask.sum())
    if affected == 0:
        return result, 0

    if action == "mark":
        flag = f"{column}_outlier"
        result[flag] = False
        result.loc[mask, flag] = True
    elif action == "remove":
        result = result.loc[~mask].copy()
    elif action == "clamp":
        values = numeric_series(result, column)
        q1, q3 = values.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        result[column] = values.clip(lower=lower, upper=upper)
    else:
        raise ValueError("Nieznana akcja dla outlierów.")

    return result, affected