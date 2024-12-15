import pandas as pd
import os
import argparse

# --- CSV-Datei laden ---
def load_csv(filename):
    try:
        # CSV-Datei lesen
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"Die Datei {filename} wurde nicht gefunden.")
        return None
    except Exception as e:
        print(f"Fehler beim Laden der CSV-Datei: {e}")
        return None

# --- Überprüfung der Spalten und Verarbeitung der Funding Fees ---
def process_funding_fees(dataframe):
    # Sicherstellen, dass alle relevanten Spalten vorhanden sind
    required_columns = ["order", "date", "coin", "futures", "type", "sum", "fee"]
    if not all(col in dataframe.columns for col in required_columns):
        print(f"Die CSV-Datei enthält nicht die erwarteten Spalten: {', '.join(required_columns)}")
        return None

    # Neue DataFrame für die aggregierten Funding Fees erstellen
    aggregated_data = {}
    remaining_transactions = []
    conversion_log = []

    # Schleife über jede Zeile der DataFrame
    for _, row in dataframe.iterrows():
        # Datum ohne Uhrzeit extrahieren
        date_only = pd.to_datetime(row["date"]).date()

        # Nur Funding Fees verarbeiten
        if row["type"] == "contract_margin_settle_fee":
            
            key = (date_only, row["futures"])

            # Aggregiere Funding Fees
            if key in aggregated_data:
                aggregated_data[key]["sum"] += row["sum"]
                aggregated_data[key]["fee"] += row["fee"]

                # Füge zur Conversion-Log hinzu
                conversion_log.append({
                    "original_order": row["order"],
                    "aggregated_order": aggregated_data[key]["order"],
                    "date": date_only,
                    "futures": row["futures"],
                    "sum_added": row["sum"],
                    "fee_added": row["fee"]
                })
            else:
                aggregated_data[key] ={
                "order": row["order"],
                "date": date_only,
                "coin": row["coin"],
                "futures": row["futures"],
                "type": "contract_margin_settle_fee",
                "sum": row["sum"],
                "fee": row["fee"]
                }

                # Initialer Log-Eintrag
                conversion_log.append({
                    "original_order": row["order"],
                    "aggregated_order": row["order"],
                    "date": date_only,
                    "futures": row["futures"],
                    "sum_added": row["sum"],
                    "fee_added": row["fee"]
                })
            
        else:
            # Andere Transaktionen beibehalten
            remaining_transactions.append(row)
    
    # Aggregierte Daten und übrige Transaktionen in DataFrames konvertieren
    aggregated_df = pd.DataFrame(aggregated_data.values())
    transactions_df = pd.DataFrame(remaining_transactions)
    conversion_df = pd.DataFrame(conversion_log)

    return transactions_df, aggregated_df, conversion_df

# --- Daten in CSV exportieren ---
def save_to_csv(dataframe, filename="aggregated_funding_fees.csv"):
    try:
        dataframe.to_csv(filename, index=False)
        print(f"Die aggregierte CSV-Datei wurde erfolgreich erstellt: {filename}")
    except Exception as e:
        print(f"Fehler beim Speichern der CSV-Datei: {e}")


if __name__ == "__main__":
    # ArgumentParser erstellen
    parser = argparse.ArgumentParser(description="Liest den übergebenen Dateipfad.")
    parser.add_argument("file_path", type=str, help="Relativer Pfad zur Datei")

    # Argumente parsen
    args = parser.parse_args()
    input_file = args.file_path

    output_file_fees = "funding_fees.csv"
    output_file_transactions = "transactions.csv"
    output_file_conversion = "conversions.csv"
    workspaceFolder = os.path.dirname(os.path.abspath(__file__))

    # CSV laden
    df = load_csv(os.path.join(workspaceFolder, input_file))
    if df is not None:

        # Daten verarbeiten
        transactions_df, fees_df, conversion_df  = process_funding_fees(df)

        if fees_df is not None:
            save_to_csv(fees_df, os.path.join(workspaceFolder, output_file_fees))
        if transactions_df is not None:
            save_to_csv(transactions_df, os.path.join(workspaceFolder, output_file_transactions))
        if conversion_df is not None:
            save_to_csv(conversion_df, os.path.join(workspaceFolder, output_file_conversion))
