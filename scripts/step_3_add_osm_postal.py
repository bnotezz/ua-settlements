import csv
import json
import os

def add_osm_postal():
    """Adds osm_id and postal_code from ua-name-places.csv."""
    data_file = os.path.join("assets", "data", "settlements.json")
    places_file = os.path.join("assets", "ua-name-places.csv")

    # 1. Create a mapping from KATOTTH to (osm_id, postal_code)
    places_map = {}
    try:
        with open(places_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get('katotth'):
                    places_map[row['katotth']] = {
                        "osm_id": row.get('osm_id'),
                        "koatuu": row.get('koatuu'),
                        "postal_code": row.get('postal_code')
                    }
    except FileNotFoundError:
        print(f"Warning: {places_file} not found. Skipping this step.")
        return

    # 2. Load existing settlements data
    with open(data_file, 'r', encoding='utf-8') as f:
        settlements = json.load(f)

    # 3. Add osm_id and postal_code to each settlement
    for settlement in settlements:
        place_data = places_map.get(settlement["katotth_id"])
        if place_data:
            if place_data["osm_id"]:
                settlement["osm_id"] = place_data["osm_id"]
            if place_data["postal_code"]:
                settlement["postal_code"] = place_data["postal_code"]

    # 4. Write the updated data back
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(settlements, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    add_osm_postal()
    print("OSM and Postal Code data added successfully.")