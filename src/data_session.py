
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

import pandas as pd

from .data_cleaning import (
    apply_outliers,
    apply_range,
    convert_numeric_column,
    impute_missing,
    range_mask,
)


@dataclass
class DataSession:
    raw: pd.DataFrame
    current: pd.DataFrame = field(init=False)
    audit_log: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self.raw = self.raw.copy(deep=True)
        self.current = self.raw.copy(deep=True)

    @classmethod
    def from_csv(cls, path: Path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Nie znaleziono pliku: {path}")
        if path.suffix.lower() != ".csv":
            raise ValueError("Oczekiwano pliku CSV.")
        try:
            df = pd.read_csv(
                path,
                sep=None,
                engine="python",
                encoding="utf-8-sig",
            )
        except UnicodeDecodeError:
            df = pd.read_csv(
                path,
                sep=None,
                engine="python",
                encoding="latin1",
            )

        if df.empty:
            raise ValueError("Plik CSV jest pusty.")
        if len(df.columns) < 1:
            raise ValueError("Plik nie zawiera żadnej kolumny.")
        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed:")]

        return cls(df)

    def profile(self) -> pd.DataFrame:
        return pd.DataFrame({
            "typ": self.current.dtypes.astype(str),
            "braki": self.current.isna().sum(),
            "braki_%": (
                self.current.isna().mean() * 100
            ).round(2),
            "unikalne": self.current.nunique(
                dropna=True
            )
        })

    def statistics(self) -> pd.DataFrame:
        return self.current.describe(
            include="all"
        ).transpose()

    def shape(self) -> tuple[int, int]:
        return int(self.current.shape[0]), int(self.current.shape[1])

    def count_duplicates(self) -> int:
        return int(
            self.current.duplicated().sum()
        )

    def drop_duplicates(self) -> int:
        before = len(self.current)

        self.current = (
            self.current.drop_duplicates().copy()
        )

        removed = before - len(self.current)

        self._audit(
            "Usuwanie pełnych duplikatów",
            before,
            len(self.current),
            removed,
        )

        return removed

    def impute_missing(
        self,
        column: str,
        strategy: str,
        constant: object = None,
    ) -> int:
        before_rows = len(self.current)
        before_missing = int(self.current[column].isna().sum()) if column in self.current else 0
        result, affected = impute_missing(self.current, column, strategy, constant)
        self.current = result
        if affected:
            self._audit(
                f"Braki: {strategy}",
                before_rows,
                len(self.current),
                affected,
                {"kolumna": column, "braki_przed": before_missing, "stała": constant},
            )
        return affected

    def convert_numeric(self, column: str) -> int:
        before = len(self.current)
        result, invalid = convert_numeric_column(self.current, column)
        self.current = result
        self._audit(
            "Konwersja na liczby",
            before,
            len(self.current),
            invalid,
            {"kolumna": column, "wartosci_bledne_lub_nienumeryczne": invalid},
        )
        return invalid

    def range_report(
        self,
        column: str,
        minimum: float | None,
        maximum: float | None,
    ) -> int:
        if column not in self.current:
            raise ValueError(f"Nie znaleziono kolumny '{column}'.")
        affected = int(range_mask(self.current, column, minimum, maximum).sum())
        before = len(self.current)
        self._audit(
            "Wykrycie wartości poza zakresem",
            before,
            len(self.current),
            affected,
            {"kolumna": column, "min": minimum, "max": maximum},
        )
        return affected

    def apply_range(
        self,
        column: str,
        minimum: float | None,
        maximum: float | None,
        action: str,
    ) -> int:
        before = len(self.current)
        result, affected = apply_range(self.current, column, minimum, maximum, action)
        self.current = result
        if affected:
            self._audit(
                f"Zakres: {action}",
                before,
                len(self.current),
                affected,
                {"kolumna": column, "min": minimum, "max": maximum},
            )
        return affected

    def outlier_report(self, column: str, factor: float = 1.5) -> int:
        from .data_cleaning import iqr_mask
        if column not in self.current:
            raise ValueError(f"Nie znaleziono kolumny '{column}'.")
        affected = int(iqr_mask(self.current, column, factor).sum())
        before = len(self.current)
        self._audit(
            "Wykrycie outlierów IQR",
            before,
            before,
            affected,
            {"kolumna": column, "czynnik": factor},
        )
        return affected

    def apply_outliers(self, column: str, factor: float, action: str) -> int:
        before = len(self.current)
        result, affected = apply_outliers(self.current, column, factor, action)
        self.current = result
        if affected:
            self._audit(
                f"Outliery IQR: {action}",
                before,
                len(self.current),
                affected,
                {"kolumna": column, "czynnik": factor},
            )
        return affected

    def _audit(
        self,
        operation: str,
        before: int,
        after: int,
        changed: int,
        params: dict | None = None,
    ) -> None:
        self.audit_log.append({
            "czas": datetime.now().isoformat(timespec="seconds"),
            "operacja": operation,
            "przed": before,
            "po": after,
            "zmienione": changed,
            "parametry": params or {},
        })

    def export_report(self, path: str | Path) -> None:
        report = pd.DataFrame(self.audit_log)
        report.to_csv(Path(path), index=False)

    def export_csv(self, path: str | Path) -> None:
        self.current.to_csv(Path(path), index=False)

    def reset(self):
        before = len(self.current)
        self.current = self.raw.copy(deep=True)
        self._audit(
            "Przywrócenie danych surowych",
            before,
            len(self.current),
            0,
        )
