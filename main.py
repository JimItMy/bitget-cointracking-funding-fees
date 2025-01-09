import csv
import os
import argparse
from datetime import datetime

def process_csv(input_file, output_file):
    # CSV-Datei einlesen
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        headers = next(reader)  # Erste Zeile: Header
        rows = list(reader)

    # Spaltenindizes ermitteln
    typ_idx = headers.index("Typ")
    kauf_idx = headers.index("Kauf")
    cur_kauf_idx = headers.index("Cur.")  # Erster "Cur." für Kauf
    verkauf_idx = headers.index("Verkauf")
    cur_verkauf_idx = headers.index("Cur.", cur_kauf_idx + 1)  # Zweiter "Cur." für Verkauf
    gebuehr_idx = headers.index("Gebühr")
    cur_gebuehr_idx = headers.index("Cur.", cur_verkauf_idx + 1)  # Dritter "Cur." für Gebuehr
    boerse_idx = headers.index("Börse")
    gruppe_idx = headers.index("Gruppe")
    kommentar_idx = headers.index("Kommentar")
    datum_idx = headers.index("Datum")

    # Ergebnis-Liste initialisieren
    processed_rows = []
    grouped_data_out = {}
    grouped_data_in = {}

    for row in rows:
        # Typ und Datum extrahieren
        typ = row[typ_idx]
        datum = datetime.strptime(row[datum_idx], '%d.%m.%Y %H:%M:%S').date()

        if typ == 'Sonstige Gebühr':
            # Gruppieren nach Datum
            if datum not in grouped_data_out:
                grouped_data_out[datum] = {
                    typ_idx: typ,
                    kauf_idx: '',
                    cur_kauf_idx: '',
                    verkauf_idx: float(row[verkauf_idx]),
                    cur_verkauf_idx: row[cur_verkauf_idx],
                    gebuehr_idx: '',
                    boerse_idx: row[boerse_idx],
                    gruppe_idx: row[gruppe_idx],
                    kommentar_idx: row[kommentar_idx],
                    datum_idx: datum.strftime('%d.%m.%Y 00:00:00'),
                }
            else:
                # Verkauf aufaddieren
                grouped_data_out[datum][verkauf_idx] += float(row[verkauf_idx])

        elif type == 'Sonstige Einnahme':
            if datum not in grouped_data_in:
                grouped_data_in[datum] = {
                    typ_idx: typ,
                    kauf_idx: float(row[kauf_idx]),
                    cur_kauf_idx: row[cur_kauf_idx],
                    verkauf_idx: '',
                    cur_verkauf_idx: '',
                    gebuehr_idx: '',
                    boerse_idx: row[boerse_idx],
                    gruppe_idx: row[gruppe_idx],
                    kommentar_idx: row[kommentar_idx],
                    datum_idx: datum.strftime('%d.%m.%Y 00:00:00'),
                }
            else:
                grouped_data_in[datum][kauf_idx] += float(row[kauf_idx])

        else:
            # row[datum_idx] = datum.strftime('%d.%m.%Y 00:00:00')  
            processed_rows.append(row)

    # Zusammengefasste "Sonstige Gebühr"-Daten hinzufügen
    for datum, grouped_row_out in grouped_data_out.items():
        new_row = [None] * len(headers)
        for col_idx, value in grouped_row_out.items():
            new_row[col_idx] = value
        processed_rows.append(new_row)
    
    for datum, grouped_row_in in grouped_data_in.items():
        new_row = [None] * len(headers)
        for col_idx, value in grouped_row_in.items():
            new_row[col_idx] = value
        processed_rows.append(new_row)

    # Reihenfolge der Zeilen nach Datum absteigend sortieren
    processed_rows.sort(key=lambda x: datetime.strptime(x[datum_idx], '%d.%m.%Y %H:%M:%S'), reverse=True)

    # CSV-Datei schreiben
    with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(headers)
        writer.writerows(processed_rows)



if __name__ == "__main__":
    # ArgumentParser erstellen
    parser = argparse.ArgumentParser(description="Liest den übergebenen Dateipfad.")
    parser.add_argument("file_path", type=str, help="Relativer Pfad zur Datei")

    # Argumente parsen
    args = parser.parse_args()
    input_file = args.file_path

    output_file = "output.csv"
    workspaceFolder = os.path.dirname(os.path.abspath(__file__))

    # Aufruf der Funktion
    process_csv(
        os.path.join(workspaceFolder, input_file),
        os.path.join(workspaceFolder, output_file),
     )
