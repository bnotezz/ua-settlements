import csv
import json
import os
import logging
from categories import get_category_name, get_admin_level

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_settlements():
    """
    Generates the initial settlements.json file from the KATOТTH kodifikator.
    """
    base_path = os.path.join("assets", "kodifikator")
    kodifikator_file = os.path.join(base_path, "kodifikator-02-07-2025.csv")
    output_file = os.path.join("assets", "data", "settlements.json")

    settlements = []
    with open(output_file, 'r', encoding='utf-8') as f:
        settlements = json.load(f)

    with open(kodifikator_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        header = next(reader) # Skip header
        
        settlements_dict = dict()

        for row in reader:
            # Ensure row has enough columns to prevent IndexError
            if len(row) < 7:
                print(f"Skipping row with insufficient columns: {row}")
                continue

            category = row[5]

            katotth_hierarchy = [elem.strip() for elem in [row[0], row[1], row[2], row[3], row[4]] if elem.strip()]
            katotth_id = len(katotth_hierarchy) > 0 and katotth_hierarchy[-1] or None
            parent_katotth = len(katotth_hierarchy) > 1 and katotth_hierarchy[-2] or None

            if katotth_id:
                settlement = {"katotth_id": katotth_id}
                for existing in settlements:
                    if existing.get("katotth_id") == katotth_id:
                        settlement = existing
                        break
                
                if not settlement:
                    settlement = {"katotth_id": katotth_id}
                    settlements.append(settlement)

                parent_katotth = parent_katotth
                settlement["name"] = row[6].strip()
                settlement["category"] = category
                settlement["type"] = get_category_name(category)

                settlements_dict[katotth_id] = settlement["name"]

                admin_level = get_admin_level(settlement)
                settlement["admin_level"] = f"{admin_level}"

                if((admin_level == 2 or admin_level == 3 or admin_level == 4) and len(katotth_hierarchy) > 1):
                    settlement["oblast_id"] = katotth_hierarchy[0]

                if((admin_level == 3 or admin_level == 4) and len(katotth_hierarchy) > 2):
                    settlement["district_id"] = katotth_hierarchy[1]
                
                if((admin_level == 4) and len(katotth_hierarchy) > 3):
                    settlement["hromada_id"] = katotth_hierarchy[2]

                if(parent_katotth):
                    settlement["parent_katotth"] = parent_katotth
                
            else:
                logger.warning(f"Skipping row with missing katotth_id: {row}")

    for settlement in settlements:
        oblast_id = settlement.get("oblast_id")
        if(oblast_id and settlements_dict.get(oblast_id)):
            settlement["oblast_name"] = settlements_dict[oblast_id]

        district_id = settlement.get("district_id")
        if(district_id and settlements_dict.get(district_id)):
            settlement["district_name"] = settlements_dict[district_id]
        hromada_id = settlement.get("hromada_id")
        if(hromada_id and settlements_dict.get(hromada_id)):
            settlement["hromada_name"] = settlements_dict[hromada_id]

    # Save the settlements data to the output file
    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(settlements, jsonfile, ensure_ascii=False, indent=2)
        logger.info(f"Generated settlements.json with {len(settlements)} entries.")

if __name__ == '__main__':
    generate_settlements()
    