import json
import os
import logging
from categories import  is_area_type, is_point_type, get_category_name, get_admin_level, ALL_TYPES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_duplicates(settlements):
    """
    Find duplicate settlements based on their administrative IDs.
    """
    katotth = dict()
    koatuu = dict()
    wikidata = dict()

    for settlement in settlements:
        name = settlement.get("name")
        katotth_id = settlement.get("katotth_id")
        koatuu_id = settlement.get("koatuu_id")
        wikidata_id = settlement.get("wikidata")

        el = {"name":name, "katotth_id": katotth_id}
        if katotth_id in katotth:
            katotth[katotth_id].append(el)
        else:
            katotth[katotth_id] = [el]

        if koatuu_id:
            if koatuu_id in koatuu:
                koatuu[koatuu_id].append(el)
            else:
                koatuu[koatuu_id] = [el] 
        if wikidata_id:    
            if wikidata_id in wikidata:
                wikidata[wikidata_id].append(el)
            else:
                wikidata[wikidata_id] = [el]

    drop_wikidata_for = set()
    for id, elements in katotth.items():
        if len(elements) > 1:
            logger.warning(f"Duplicate katotth_id {id} found for settlements: {', '.join(el.get('name', 'Unknown') for el in elements)}")
    # for id, elements in koatuu.items():
    #     if len(elements) > 1:
    #         logger.warning(f"Duplicate koatuu_id {id} found for settlements: {', '.join(el.get('name', 'Unknown') for el in elements)}")
    for id, elements in wikidata.items():
        if len(elements) > 1:
            drop_wikidata_for.add(id)
            logger.warning(f"Duplicate wikidata_id {id} found for settlements: {', '.join(el.get('name', 'Unknown') for el in elements)}")

    need_to_drop_duplicates = False
    for settlement in settlements:
        # if settlement.get("koatuu_id") in drop_koatuu_for:
        #     need_to_drop_duplicates = True
        #     settlement.pop("koatuu_id", None)
        #     logger.info(f"Removed koatuu_id for settlement {settlement.get('name')}")
        if settlement.get("wikidata") in drop_wikidata_for:
            need_to_drop_duplicates = True
            settlement.pop("wikidata", None)
            logger.info(f"Removed wikidata_id for settlement {settlement.get('name')}")
    if need_to_drop_duplicates:
        logger.info("Duplicates found and removed. Saving updated settlements data.")
        data_file = os.path.join("assets", "data", "settlements.json")
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(settlements, f, ensure_ascii=False, indent=2)

def validate_maps(settlements):
    oblasti_map_file = os.path.join("assets", "maps", "ukraine_oblasti.geojson")
    with open(oblasti_map_file, 'r', encoding='utf-8') as f:
        oblasti_map = json.load(f)
    
    districts_map_file = os.path.join("assets", "maps", "districts.geojson")
    with open(districts_map_file, 'r', encoding='utf-8') as f:
        districts_map = json.load(f)

    communities_map_file = os.path.join("assets", "maps", "communities.geojson")
    with open(communities_map_file, 'r', encoding='utf-8') as f:
        communities_map = json.load(f)

    for settlement in settlements:
        category = settlement.get("category")
        if get_admin_level(settlement) == 1:
            map_item_found = False
            for oblast in oblasti_map["features"]:
                if settlement.get("katotth_id") == oblast.get("properties", {}).get("katotth"):
                    map_item_found = True
                    break
            if not map_item_found:
                logger.warning(f"Oblast {settlement.get('katotth_id')} {settlement.get('name')} not found in oblasts map.")
        if category == "P":
            map_item_found = False
            for disctrict in districts_map["features"]:
                if settlement.get("katotth_id") == disctrict.get("properties", {}).get("katotth"):
                    map_item_found = True
                    break
            if not map_item_found:
                logger.warning(f"District {settlement.get('katotth_id')} {settlement.get('name')} not found in districts map.")
        if category == "H":
            map_item_found = False
            for community in communities_map["features"]:
                if settlement.get("katotth_id") == community.get("properties", {}).get("katotth"):
                    map_item_found = True
                    break
            if not map_item_found:
                logger.warning(f"Community {settlement.get('katotth_id')} {settlement.get('name')} not found in communities map.")

def check_generated_data():
    data_file = os.path.join("assets", "data", "settlements.json")
    with open(data_file, 'r', encoding='utf-8') as f:
        settlements = json.load(f)

    settlements_count = len(settlements)
    logger.info(f"Total settlements and regions loaded: {settlements_count}")


    
    missing_data = {
        "osm_id": {type_: 0 for type_ in ALL_TYPES},
        "postal_code": {type_: 0 for type_ in ALL_TYPES},
        "location": {type_: 0 for type_ in ALL_TYPES},
        "koatuu_id": {type_: 0 for type_ in ALL_TYPES},
        "wikidata": {type_: 0 for type_ in ALL_TYPES},
    }

    regions_settlements = 0
    settlements_count = 0
    for settlement in settlements:
        is_region = is_area_type(settlement)
        is_settlement = is_point_type(settlement)

        if not settlement.get("name"):
            logger.warning(f"Settlement {settlement.get('katotth_id')} has no name.")
        if not settlement.get("category"):
            logger.warning(f"Settlement {settlement.get('katotth_id')} has no category.")
        if not settlement.get("osm_id"):
            missing_data["osm_id"][settlement.get("category")] += 1
        if not settlement.get("postal_code"):
            missing_data["postal_code"][settlement.get("category")] += 1
        if not settlement.get("wikidata"):
            missing_data["wikidata"][settlement.get("category")] += 1
            if is_settlement:
                logger.warning(f"Settlement {settlement.get('katotth_id')} - {settlement.get('name')} has no Wikidata ID.")
        if not settlement.get("location"):
            missing_data["location"][settlement.get("category")] += 1
        if not settlement.get("koatuu_id"):
            missing_data["koatuu_id"][settlement.get("category")] += 1
            if not is_region:
                logger.warning(f"Settlement {settlement.get('katotth_id')} - {settlement.get('name')} has no KOATUU ID.")
        if is_region:
            regions_settlements += 1
        if is_settlement:
            settlements_count += 1

    
    validate_maps(settlements)

    find_duplicates(settlements)
    
    for type_ in ALL_TYPES:
        cat_name =get_category_name(type_)
        for missing_type, missing_records in missing_data.items():
            if missing_records[type_] > 0:
                logger.warning(f"'{cat_name}' has no {missing_type.replace('_', ' ')}: {missing_records[type_]}")
  
    logger.info(f"Regions Settlements Count: {regions_settlements}")
    logger.info(f"Regions Settlements: {regions_settlements}")
    logger.info(f"Settlements: {settlements_count}")


