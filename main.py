import csv
import os
import argparse
from datetime import datetime

def parse_date(date_str):
    for fmt in ('%d.%m.%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unbekanntes Datumsformat: {date_str}")

def process_csv(input_file, output_file):
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        headers = next(reader)
        rows = list(reader)

    typ_idx = headers.index("Type")
    kauf_idx = headers.index("Buy")
    cur_kauf_idx = headers.index("Cur.")
    verkauf_idx = headers.index("Sell")
    cur_verkauf_idx = headers.index("Cur.", cur_kauf_idx + 1)
    gebuehr_idx = headers.index("Fee")
    cur_gebuehr_idx = headers.index("Cur.", cur_verkauf_idx + 1)
    boerse_idx = headers.index("Exchange")
    gruppe_idx = headers.index("Group")
    kommentar_idx = headers.index("Comment")
    datum_idx = headers.index("Date")

    processed_rows = []
    grouped_data_out = {}   # Other Fee: key = datum
    grouped_data_in = {}    # Other Income: key = datum
    grouped_interest = {}   # Interest Income: key = (datum, währung)
    grouped_bonus = {}      # Reward / Bonus: key = (datum, währung)

    # Typen die zusammengefasst werden
    GROUPED_TYPES = {'Other Fee', 'Other Income', 'Interest Income', 'Reward / Bonus'}

    for row in rows:
        typ = row[typ_idx]
        datum = parse_date(row[datum_idx]).date()

        if typ == 'Other Fee':
            sell_val = float(row[verkauf_idx]) if row[verkauf_idx] else 0.0
            if datum not in grouped_data_out:
                grouped_data_out[datum] = {
                    typ_idx: typ,
                    kauf_idx: '',
                    cur_kauf_idx: '',
                    verkauf_idx: sell_val,
                    cur_verkauf_idx: 'USDT',
                    gebuehr_idx: '',
                    cur_gebuehr_idx: '',
                    boerse_idx: row[boerse_idx],
                    gruppe_idx: row[gruppe_idx],
                    kommentar_idx: row[kommentar_idx],
                    datum_idx: datum.strftime('%d.%m.%Y 00:00:00'),
                }
            else:
                grouped_data_out[datum][verkauf_idx] += sell_val

        elif typ == 'Other Income':
            buy_val = float(row[kauf_idx]) if row[kauf_idx] else 0.0
            if datum not in grouped_data_in:
                grouped_data_in[datum] = {
                    typ_idx: typ,
                    kauf_idx: buy_val,
                    cur_kauf_idx: 'USDT',
                    verkauf_idx: '',
                    cur_verkauf_idx: '',
                    gebuehr_idx: '',
                    cur_gebuehr_idx: '',
                    boerse_idx: row[boerse_idx],
                    gruppe_idx: row[gruppe_idx],
                    kommentar_idx: row[kommentar_idx],
                    datum_idx: datum.strftime('%d.%m.%Y 00:00:00'),
                }
            else:
                grouped_data_in[datum][kauf_idx] += buy_val

        elif typ == 'Interest Income':
            buy_val = float(row[kauf_idx]) if row[kauf_idx] else 0.0
            currency = row[cur_kauf_idx]
            key = (datum, currency)
            if key not in grouped_interest:
                grouped_interest[key] = {
                    typ_idx: typ,
                    kauf_idx: buy_val,
                    cur_kauf_idx: currency,
                    verkauf_idx: '',
                    cur_verkauf_idx: '',
                    gebuehr_idx: '',
                    cur_gebuehr_idx: '',
                    boerse_idx: row[boerse_idx],
                    gruppe_idx: row[gruppe_idx],
                    kommentar_idx: row[kommentar_idx],
                    datum_idx: datum.strftime('%d.%m.%Y 00:00:00'),
                }
            else:
                grouped_interest[key][kauf_idx] += buy_val

        elif typ == 'Reward / Bonus':
            buy_val = float(row[kauf_idx]) if row[kauf_idx] else 0.0
            currency = row[cur_kauf_idx]
            key = (datum, currency)
            if key not in grouped_bonus:
                grouped_bonus[key] = {
                    typ_idx: typ,
                    kauf_idx: buy_val,
                    cur_kauf_idx: currency,
                    verkauf_idx: '',
                    cur_verkauf_idx: '',
                    gebuehr_idx: '',
                    cur_gebuehr_idx: '',
                    boerse_idx: row[boerse_idx],
                    gruppe_idx: row[gruppe_idx],
                    kommentar_idx: row[kommentar_idx],
                    datum_idx: datum.strftime('%d.%m.%Y 00:00:00'),
                }
            else:
                grouped_bonus[key][kauf_idx] += buy_val

        else:
            processed_rows.append(row)

    for grouped in [grouped_data_out, grouped_data_in, grouped_interest, grouped_bonus]:
        for key, grouped_row in grouped.items():
            new_row = [''] * len(headers)
            for col_idx, value in grouped_row.items():
                new_row[col_idx] = value
            processed_rows.append(new_row)

    processed_rows.sort(
        key=lambda x: parse_date(x[datum_idx]),
        reverse=True
    )

    with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(headers)
        writer.writerows(processed_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Liest den übergebenen Dateipfad.")
    parser.add_argument("file_path", type=str, help="Relativer Pfad zur Datei")

    args = parser.parse_args()
    input_file = args.file_path
    output_file = "output.csv"
    workspaceFolder = os.path.dirname(os.path.abspath(__file__))

    process_csv(
        os.path.join(workspaceFolder, input_file),
        os.path.join(workspaceFolder, output_file),
    )
