import csv

def load_csv_file_as_list(file_path: str, encoding: str = "utf-8") -> list[list[str]]:
    """Liest eine CSV-Datei zeilenweise in eine Liste von Zeilen (jede Zeile = Liste von Zellen)."""
    with open(file_path, "r", encoding=encoding) as file:
        reader = csv.reader(file)
        return list(reader)


def load_csv_file_as_dict(file_path: str, encoding: str = "utf-8") -> dict[str, str]:
    """
    Liest eine CSV-Datei als ein einziges Dict (erste Spalte = Key, zweite Spalte = Value).
    Nur für 2-Spalten-CSVs geeignet; bei mehr Spalten werden nur die ersten beiden genutzt.
    Für CSV mit Header und mehreren Spalten besser load_csv_file_as_list_of_dicts nutzen.
    """
    with open(file_path, "r", encoding=encoding) as file:
        reader = csv.reader(file)
        return {row[0]: row[1] for row in reader if len(row) >= 2}


def load_csv_file_as_list_of_dicts(file_path: str, encoding: str = "utf-8") -> list[dict[str, str]]:
    """Liest eine CSV-Datei mit Header-Zeile; jede Zeile wird ein Dict (Spaltenname -> Wert)."""
    with open(file_path, "r", encoding=encoding) as file:
        return list(csv.DictReader(file))
