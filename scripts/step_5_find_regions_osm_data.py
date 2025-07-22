import json
import os
import time
import logging
from overpass import find_entities_by_propety
from categories import is_area_type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chunk_list(data, chunk_size):
    """Yield successive chunks of size chunk_size from data."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def get_regions_list(settlements):
    """
    Find regions by their administrative IDs using Overpass API.
    """
    if not settlements:
        logger.warning("No settlements provided.")
        return []

    # Extract unique administrative IDs from settlements
    admin_ids = set()  # Use a set to avoid duplicates
    admin_ids |= {settlement.get("katotth_id") for settlement in settlements if settlement.get("katotth_id") and not settlement.get("osm_id") and is_area_type(settlement)}

    if not admin_ids:
        logger.warning("No administrative IDs found in settlements.")
        return []
    # return sorted(admin_ids)  # Return a sorted list of unique IDs
    admin_ids = list(admin_ids)
    # Sort the IDs for consistency
    admin_ids.sort()
    return admin_ids


def find_osm_data(settlements):
    """
    Find regions by their administrative IDs using Overpass API.
    """
    if not settlements:
        logger.warning("No settlements provided.")
        return []

    # Extract unique administrative IDs from settlements
    admin_ids = get_regions_list(settlements)
    total_admin_ids = len(admin_ids)
    logger.info(f"Found {total_admin_ids} unique administrative IDs.")
    regions = dict()
    procedsed_admin_ids = 0
    for group in chunk_list(admin_ids, 15):
        step_start_time = time.time()
        logger.info(f"Processing Admin IDs {procedsed_admin_ids + 1} to {procedsed_admin_ids + len(group)} of {total_admin_ids}")
        procedsed_admin_ids += len(group)

        entities = find_entities_by_propety("katotth", group, logger, type="relation")
        if not entities:
            logger.warning(f"No entities found for the provided administrative IDs: {', '.join(map(str, group))}")
            continue
        else:
            logger.info(f"Found {len(entities)} entities for the provided administrative IDs")
        
        for admin_id in group:
            # Find the first entity that matches the administrative ID
            found_entities = [ent for ent in entities if ent.get("katotth_id") == admin_id]
            if not found_entities:
                logger.warning(f"No entities found for katotth_id {admin_id}")
                continue
            
            # Use the first entity found
            osm = found_entities[0]

            regions[admin_id] = osm

        step_end_time = time.time()
        logger.info(f"Processed {len(group)} admin IDs in {step_end_time - step_start_time:.2f} seconds.")

    return regions

def update_regions_data(settlements):
    """
    Update settlements with OSM data for regions based on katotth IDs.
    
    Args:
        settlements (list): List of settlement dictionaries.
    
    Returns:
        None
    """
    if not settlements:
        logger.warning("No settlements provided.")
        return

    regions = find_osm_data(settlements)
    if not regions:
        logger.warning("No regions found.")
        return
    logger.info(f"Found {len(regions)} regions with OSM data.")

    # Update the original settlements with the new location data
    for settlement in settlements:
        admin_id = settlement.get("katotth_id")
        if admin_id and admin_id in regions:
            location_data = regions[admin_id]
            for k,v in location_data.items():
                if k != "katotth_id" and k != "koatuu_id" and v is not None:
                    settlement[k] = v

    save_settlements(settlements)

def save_settlements(settlements):
    data_file = os.path.join("assets", "data", "settlements.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(settlements, f, ensure_ascii=False, indent=2)

def find_regions_osm_data():
    """Finds and adds osm data for regions based on katotth ids."""
    data_file = os.path.join("assets", "data", "settlements.json")

    with open(data_file, 'r', encoding='utf-8') as f:
        settlements = json.load(f)

    update_regions_data(settlements)
    logger.info("OSM data fetching complete.")

if __name__ == '__main__':
    find_regions_osm_data()
