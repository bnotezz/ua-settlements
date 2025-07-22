import csv
import json
import os

def map_comparison_table():
    """Maps KOATUU IDs to the settlements from the comparison table."""
    data_file = os.path.join("assets", "data", "settlements.json")
    comparison_file = os.path.join("assets", "kodifikator", "Порівняльна таблиця.csv")

    # 1. Create a mapping from KATOTTH to KOATUU
    koatuu_map = {}
    with open(comparison_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        header = next(reader) # Skip header
        for row in reader:
            if len(row) >= 2:
                katotth_id, koatuu_id = row[:2]
                if katotth_id and koatuu_id and koatuu_id.isdigit():
                    koatuu_map[str(katotth_id)] = str(koatuu_id)

    # 2. Load existing settlements data
    with open(data_file, 'r', encoding='utf-8') as f:
        settlements = json.load(f)

    # 3. Add koatuu_id to each settlement if found
    for settlement in settlements:
        katotth_id = settlement.get("katotth_id")
        if katotth_id in koatuu_map:
            settlement["koatuu_id"] = koatuu_map[katotth_id]

    # 4. Write the updated data back to the file
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(settlements, f, ensure_ascii=False, indent=2)

def map_koatuu():
   map_comparison_table()


if __name__ == '__main__':
    map_koatuu()
    print("KOATUU IDs mapped successfully.")