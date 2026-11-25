"""Tkinter/ttk interfejs aplikacji."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from .data_session import DataSession
from .visualization import (
    bar_figure,
    box_figure,
    correlation,
    histogram_figure,
    scatter_figure,
)


class DataQualityApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Studio jakości i wizualizacji danych")
        self.geometry("1180x760")
        self.session: DataSession | None = None
        self.canvas: FigureCanvasTkAgg | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Button(top, text="Wczytaj CSV", command=self.load_csv).pack(side="left")
        ttk.Button(top, text="Wczytaj ponownie", command=self.reload_csv).pack(side="left", padx=5)
        ttk.Button(top, text="Reset do surowych", command=self.reset_session).pack(side="left")
        self.file_label = ttk.Label(top, text="Nie wczytano pliku")
        self.file_label.pack(side="left", padx=12)

        main = ttk.Panedwindow(self, orient="horizontal")
        main.pack(fill="both", expand=True, padx=8, pady=8)

        left = ttk.Notebook(main)
        right = ttk.Frame(main)
        main.add(left, weight=1)
        main.add(right, weight=3)

        self.profile_text = tk.Text(left, width=55, height=12)
        left.add(self.profile_text, text="Profil i podgląd")
        self.profile_tree = ttk.Treeview(left)
        left.add(self.profile_tree, text="Profil kolumn")

        clean = ttk.Frame(left, padding=8)
        left.add(clean, text="Czyszczenie")
        ttk.Label(clean, text="Kolumna").grid(row=0, column=0, sticky="w")
        self.column_combo = ttk.Combobox(clean, state="readonly")
        self.column_combo.grid(row=0, column=1, sticky="ew")

        ttk.Label(clean, text="Strategia braków").grid(row=1, column=0, sticky="w")
        self.missing_combo = ttk.Combobox(
            clean,
            state="readonly",
            values=["delete", "mean", "median", "mode", "constant"],
        )
        self.missing_combo.set("median")
        self.missing_combo.grid(row=1, column=1, sticky="ew")
        ttk.Label(clean, text="Stała").grid(row=2, column=0, sticky="w")
        self.constant_entry = ttk.Entry(clean)
        self.constant_entry.grid(row=2, column=1, sticky="ew")
        ttk.Button(clean, text="Imputuj / usuń braki", command=self.impute_missing).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=3
        )
        ttk.Button(clean, text="Usuń pełne duplikaty", command=self.drop_duplicates).grid(
            row=4, column=0, columnspan=2, sticky="ew"
        )

        ttk.Label(clean, text="Zakres min").grid(row=5, column=0, sticky="w")
        self.min_entry = ttk.Entry(clean)
        self.min_entry.grid(row=5, column=1, sticky="ew")
        ttk.Label(clean, text="Zakres max").grid(row=6, column=0, sticky="w")
        self.max_entry = ttk.Entry(clean)
        self.max_entry.grid(row=6, column=1, sticky="ew")
        ttk.Button(clean, text="Wykryj poza zakresem", command=self.report_range).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=3
        )
        ttk.Label(clean, text="Akcja zakresu").grid(row=8, column=0, sticky="w")
        self.range_action = ttk.Combobox(clean, state="readonly", values=["mark", "remove", "clamp"])
        self.range_action.set("mark")
        self.range_action.grid(row=8, column=1, sticky="ew")
        ttk.Button(clean, text="Zastosuj zakres", command=self.apply_range).grid(
            row=9, column=0, columnspan=2, sticky="ew"
        )

        ttk.Label(clean, text="IQR czynnik").grid(row=10, column=0, sticky="w")
        self.iqr_entry = ttk.Entry(clean)
        self.iqr_entry.insert(0, "1.5")
        self.iqr_entry.grid(row=10, column=1, sticky="ew")
        ttk.Button(clean, text="Wykryj outliery", command=self.report_outliers).grid(
            row=11, column=0, columnspan=2, sticky="ew", pady=3
        )
        ttk.Label(clean, text="Akcja outlierów").grid(row=12, column=0, sticky="w")
        self.outlier_action = ttk.Combobox(clean, state="readonly", values=["mark", "remove", "clamp"])
        self.outlier_action.set("mark")
        self.outlier_action.grid(row=12, column=1, sticky="ew")
        ttk.Button(clean, text="Zastosuj outliery", command=self.apply_outliers).grid(
            row=13, column=0, columnspan=2, sticky="ew"
        )
        ttk.Button(clean, text="Konwertuj kolumnę na liczby", command=self.convert_numeric).grid(
            row=14, column=0, columnspan=2, sticky="ew", pady=3
        )
        clean.columnconfigure(1, weight=1)

        viz = ttk.Frame(right, padding=6)
        viz.pack(fill="x")
        ttk.Label(viz, text="Typ wykresu").grid(row=0, column=0)
        self.plot_type = ttk.Combobox(
            viz,
            state="readonly",
            values=["Histogram", "Scatter", "Box plot", "Bar plot"],
        )
        self.plot_type.set("Histogram")
        self.plot_type.grid(row=0, column=1)
        ttk.Label(viz, text="Kolumna X").grid(row=0, column=2, padx=(8, 0))
        self.x_combo = ttk.Combobox(viz, state="readonly")
        self.x_combo.grid(row=0, column=3)
        ttk.Label(viz, text="Kolumna Y").grid(row=0, column=4, padx=(8, 0))
        self.y_combo = ttk.Combobox(viz, state="readonly")
        self.y_combo.grid(row=0, column=5)
        ttk.Button(viz, text="Pokaż wykres", command=self.show_plot).grid(row=0, column=6, padx=8)
        ttk.Button(viz, text="Korelacja", command=self.show_correlation).grid(row=0, column=7)

        export = ttk.Frame(right)
        export.pack(fill="x")
        ttk.Button(export, text="Zapisz cleaned.csv", command=self.export_csv).pack(side="left")
        ttk.Button(export, text="Zapisz raport zmian", command=self.export_report).pack(side="left", padx=5)
        ttk.Button(export, text="Zapisz wykres PNG", command=lambda: self.export_plot("png")).pack(side="left")
        ttk.Button(export, text="Zapisz wykres PDF", command=lambda: self.export_plot("pdf")).pack(side="left", padx=5)
        ttk.Button(export, text="Zapisz wykres SVG", command=lambda: self.export_plot("svg")).pack(side="left")

        self.plot_container = ttk.Frame(right)
        self.plot_container.pack(fill="both", expand=True)
        self.status = ttk.Label(right, text="Gotowy.")
        self.status.pack(fill="x")

    def load_csv(self) -> None:
        path = filedialog.askopenfilename(
            title="Wybierz CSV",
            filetypes=[("CSV", "*.csv"), ("Wszystkie pliki", "*.*")],
        )
        if path:
            self._load_path(Path(path))

    def reload_csv(self) -> None:
        if not hasattr(self, "_source_path") or self._source_path is None:
            messagebox.showwarning("Brak pliku", "Najpierw wczytaj plik CSV.")
            return
        self._load_path(self._source_path)

    def _load_path(self, path: Path) -> None:
        try:
            self.session = DataSession.from_csv(path)
            self._source_path = path
            self.file_label.configure(text=str(path))
            self.refresh_all()
            self.status.configure(text="Wczytano poprawnie. Dane można analizować i czyszczyć.")
        except (FileNotFoundError, UnicodeDecodeError, pd.errors.ParserError, ValueError, OSError) as exc:
            messagebox.showerror("Błąd wczytywania", str(exc))
            self.status.configure(text=f"Błąd: {exc}")

    def refresh_all(self) -> None:
        if self.session is None:
            return
        columns = list(self.session.current.columns)
        for combo in (self.column_combo, self.x_combo, self.y_combo):
            combo.configure(values=columns)
        if columns:
            if not self.column_combo.get():
                self.column_combo.set(columns[0])
            if not self.x_combo.get():
                self.x_combo.set(columns[0])
            if len(columns) > 1 and not self.y_combo.get():
                self.y_combo.set(columns[1])
        self.profile_text.configure(state="normal")
        self.profile_text.delete("1.0", "end")
        rows, cols = self.session.shape()
        duplicate_count = self.session.count_duplicates()
        text = (
            f"Plik: {getattr(self, '_source_path', 'brak')}\n"
            f"Wymiary: {rows} rekordów x {cols} kolumn\n"
            f"Pełne duplikaty: {duplicate_count}\n\n"
            "Podgląd pierwszych rekordów:\n"
        )
        self.profile_text.insert("end", text)
        self.profile_text.insert("end", self.session.current.head(10).to_string())
        self.profile_text.insert("end", "\n\nProfil kolumn:\n")
        self.profile_text.insert("end", self.session.profile().to_string())
        self.profile_text.configure(state="disabled")

        for item in self.profile_tree.get_children():
            self.profile_tree.delete(item)
        self.profile_tree["columns"] = ("wartosc",)
        self.profile_tree.heading("#0", text="Operacja")
        self.profile_tree.heading("wartosc", text="Szczegóły")
        for entry in self.session.audit_log[-20:]:
            params = str(entry["parametry"])
            self.profile_tree.insert(
                "",
                "end",
                text=entry["operacja"],
                values=(f"przed={entry['przed']} po={entry['po']} zmienione={entry['zmienione']} {params}",),
            )

    def _require_session(self) -> DataSession:
        if self.session is None:
            raise ValueError("Najpierw wczytaj plik CSV.")
        return self.session

    def _selected_column(self) -> str:
        column = self.column_combo.get()
        if not column:
            raise ValueError("Wybierz kolumnę.")
        return column

    def impute_missing(self) -> None:
        try:
            session = self._require_session()
            column = self._selected_column()
            strategy = self.missing_combo.get()
            constant_text = self.constant_entry.get().strip()
            constant: object = constant_text if constant_text else None
            affected = session.impute_missing(column, strategy, constant)
            self.refresh_all()
            self.status.configure(text=f"Braki: zmieniono {affected} rekordów.")
        except (ValueError, KeyError) as exc:
            messagebox.showwarning("Nie można wykonać operacji", str(exc))

    def drop_duplicates(self) -> None:
        try:
            session = self._require_session()
            removed = session.drop_duplicates()
            self.refresh_all()
            self.status.configure(text=f"Usunięto pełne duplikaty: {removed}.")
        except ValueError as exc:
            messagebox.showwarning("Nie można wykonać operacji", str(exc))

    def _bounds(self) -> tuple[float | None, float | None]:
        minimum = float(self.min_entry.get()) if self.min_entry.get().strip() else None
        maximum = float(self.max_entry.get()) if self.max_entry.get().strip() else None
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("Dolna granica nie może być większa od górnej.")
        return minimum, maximum

    def report_range(self) -> None:
        try:
            session = self._require_session()
            minimum, maximum = self._bounds()
            affected = session.range_report(self._selected_column(), minimum, maximum)
            self.refresh_all()
            self.status.configure(text=f"Poza zakresem: {affected} rekordów.")
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("Niepoprawna reguła", str(exc))

    def apply_range(self) -> None:
        try:
            session = self._require_session()
            minimum, maximum = self._bounds()
            affected = session.apply_range(
                self._selected_column(), minimum, maximum, self.range_action.get()
            )
            self.refresh_all()
            self.status.configure(text=f"Zastosowano zakres do {affected} rekordów.")
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("Niepoprawna reguła", str(exc))

    def _iqr_factor(self) -> float:
        factor = float(self.iqr_entry.get())
        if factor <= 0:
            raise ValueError("Czynnik IQR musi być większy od zera.")
        return factor

    def report_outliers(self) -> None:
        try:
            session = self._require_session()
            affected = session.outlier_report(self._selected_column(), self._iqr_factor())
            self.refresh_all()
            self.status.configure(text=f"Wykryto outliery IQR: {affected}.")
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("Niepoprawna reguła", str(exc))

    def apply_outliers(self) -> None:
        try:
            session = self._require_session()
            affected = session.apply_outliers(
                self._selected_column(), self._iqr_factor(), self.outlier_action.get()
            )
            self.refresh_all()
            self.status.configure(text=f"Zastosowano akcję outlierów do {affected} rekordów.")
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("Niepoprawna reguła", str(exc))

    def convert_numeric(self) -> None:
        try:
            session = self._require_session()
            invalid = session.convert_numeric(self._selected_column())
            self.refresh_all()
            self.status.configure(text=f"Konwersja: znaleziono {invalid} błędnych wartości.")
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("Niepoprawna kolumna", str(exc))

    def reset_session(self) -> None:
        if self.session is None:
            messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV.")
            return
        self.session.reset()
        self.refresh_all()
        self.status.configure(text="Przywrócono dane surowe.")

    def show_plot(self) -> None:
        try:
            session = self._require_session()
            plot_type = self.plot_type.get()
            x_column = self.x_combo.get()
            y_column = self.y_combo.get()
            if not x_column:
                raise ValueError("Wybierz kolumnę wykresu.")
            if plot_type == "Histogram":
                figure = histogram_figure(session, x_column)
            elif plot_type == "Scatter":
                if not y_column:
                    raise ValueError("Scatter wymaga kolumny X i Y.")
                figure = scatter_figure(session, x_column, y_column)
            elif plot_type == "Box plot":
                figure = box_figure(session, x_column)
            else:
                figure = bar_figure(session, x_column)
            self._display_figure(figure)
            self.status.configure(text="Wykres osadzony w oknie.")
        except (ValueError, KeyError) as exc:
            messagebox.showwarning("Niepoprawny wykres", str(exc))

    def show_correlation(self) -> None:
        try:
            session = self._require_session()
            table, description = correlation(session)
            figure = __import__("matplotlib.figure", fromlist=["Figure"]).Figure(
                figsize=(7, 4), dpi=100
            )
            axis = figure.add_subplot()
            image = axis.imshow(table.to_numpy(), cmap="coolwarm", vmin=-1, vmax=1)
            axis.set_xticks(range(len(table.columns)), table.columns, rotation=45, ha="right")
            axis.set_yticks(range(len(table.index)), table.index)
            axis.set_title("Macierz korelacji")
            figure.colorbar(image, ax=axis)
            figure.tight_layout()
            self._display_figure(figure)
            messagebox.showinfo("Interpretacja korelacji", description)
        except (ValueError, KeyError) as exc:
            messagebox.showwarning("Korelacja", str(exc))

    def _display_figure(self, figure) -> None:
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        self.canvas = FigureCanvasTkAgg(figure, master=self.plot_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def export_csv(self) -> None:
        if self.session is None:
            messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )
        if path:
            try:
                self.session.export_csv(path)
                self.status.configure(text=f"Zapisano CSV: {path}")
            except OSError as exc:
                messagebox.showerror("Błąd zapisu", str(exc))

    def export_report(self) -> None:
        if self.session is None:
            messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )
        if path:
            try:
                self.session.export_report(path)
                self.status.configure(text=f"Zapisano raport: {path}")
            except OSError as exc:
                messagebox.showerror("Błąd zapisu", str(exc))

    def export_plot(self, extension: str) -> None:
        if self.canvas is None:
            messagebox.showwarning("Brak wykresu", "Najpierw pokaż wykres.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=f".{extension}",
            filetypes=[(extension.upper(), f"*.{extension}")],
        )
        if path:
            try:
                self.canvas.figure.savefig(path)
                self.status.configure(text=f"Zapisano wykres: {path}")
            except (OSError, ValueError) as exc:
                messagebox.showerror("Błąd zapisu", str(exc))


DataQualityAppSession = DataSession


def run_app() -> None:
    app = DataQualityApp()
    app.mainloop()