# Data Quality Studio

Projekt desktopowy dla przedmiotu Programowanie V. Aplikacja prowadzi od wczytania CSV przez profil i czyszczenie do wizualizacji i eksportu.

## Wymagania

- Python 3.10 lub nowszy
- Tkinter/ttk
- pandas
- matplotlib

Na Windows łącznie z Pythonem zwykle jest dostępny Tkinter. Na niektórych dystrybucjach Linux może być potrzebny `python3-tk`.

## Instalacja i uruchomienie

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

## Funkcje

- Detekcja separatora przecinka lub średnika i fallback kodowania utf-8-latin1.
- Podgląd danych, rozmiar, typy, statystyki, braki, duplikaty i unikalność.
- Usuwanie duplikatów.
- Strategie braków: delete, mean, median, mode i constant.
- Konwersja kolumny na liczby z raportowaniem wartości błędnych.
- Reguła zakresu: wykrycie, oznaczenie, przycięcie albo usunięcie.
- Outliery IQR: wykrycie, oznaczenie, przycięcie albo usunięcie.
- Reset do kopii danych surowych bez ponownego uruchamiania aplikacji.
- Histogram, scatter, box plot i bar plot oraz macierz korelacji.
- Eksport cleaned.csv, raportu CSV i wykresów PNG/PDF/SVG.

## Interpretacja outlierów

Domyślnie IQR oznacza wartość jako outlier, gdy jest poniżej `Q1 - 1.5*IQR` lub ponad `Q3 + 1.5*IQR`. Dzieje się to dopiero po decyzji użytkownika. Oznaczenie zachowuje obserwację, przycięcie ogranicza ją do granic IQR, a usunięcie usuwa wiersz. Wartość skrajna może być błędem pomiarowym albo poprawną obserwacją; korelacja nie oznacza przyczynowości.

## Dane testowe

- `test_01_przecinek.csv` — CSV z przecinkiem.
- `test_02_srednik.csv` — CSV ze średnikiem.
- `test_03_braki_duplikaty.csv` — braki liczbowe i pełny duplikat.
- `test_04_zakres_outlier.csv` — wartość -5 i 1000 poza typowym zakresem.
- `test_05_bledne_wiersze.csv` — dodatkowa kolumna w wadliwym wierszu.
- `test_06_stala_tekst.csv` — stała i kolumna tekstowa.

## Testy

```bash
python -m pytest -q
```

Testy automatyczne znajdują się w `tests/`. Pokrywają separator, profil, braki, duplikaty, reset, zakres, IQR, konwersję i wszystkie typy wykresów. Test GUI i ponownego odczytu eksportu jest opisany w `tests/test_gui_smoke.md`.

## Znane ograniczenia

- Detekcja separatora opiera się na silniku `python` i może potrzebować dostosowania dla niestandardowych plików.
- Wadliwe wiersze nie są automatycznie naprawiane; aplikacja pokazuje błąd, jeśli parser nie może odczytać struktury.
- Stała imputacja tekstowa/literowa jest przechowywana bez automatycznej konwersji typu.

## Autorzy i źródła

- Autor: uzupełnij nazwisko i numer grupy.
- Biblioteki: pandas, Matplotlib, Tkinter/ttk.
- Dokumentacja pandas: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- Pandas User Guide: https://pandas.pydata.org/docs/user_guide/index.html
- Embed in Tk: https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
- Matplotlib: https://matplotlib.org/
