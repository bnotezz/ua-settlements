import json
import os
import time
import requests
import logging
from overpass import find_nodes_by_osm_ids

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chunk_list(data, chunk_size):
    """Yield successive chunks of size chunk_size from data."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


    
def update_settlements_locations(settlements):
    """
    Process a list of settlements in chunks, make an HTTP POST request for each chunk,
    and update each settlement with the location data returned from the API.
    
    Args:
        settlements (list): List of settlement names.
        api_url (str): URL of the API endpoint to get location data.
    
    Returns:
        list: List of dictionaries with updated settlement data.
    """

    # Filter out settlements that do not have an OSM ID and prepare new list with key "osm_id" and "location" as value
    osm_data = [{"osm_id": settlement.get("osm_id")} for settlement in settlements if settlement.get("osm_id") and not settlement.get("location")]
    # filter  out osm_ids with prefix "w" or "r" as they are not nodes
    osm_data = [osm for osm in osm_data if not osm["osm_id"].startswith(('w', 'r'))]
    # remove prefix "n" from osm_id if it exists
    for osm in osm_data:
        if osm["osm_id"].startswith('n'):
            osm["osm_id"] = osm["osm_id"][1:]

    total_osm_ids = len(osm_data)
    logger.info(f"Total OSM IDs to process: {total_osm_ids}")
    procedsed_osm_ids = 0
    bad_osm_ids = []
    for group in chunk_list(osm_data, 15):
        step_start_time = time.time()
        logger.info(f"Processing OSM IDs {procedsed_osm_ids + 1} to {procedsed_osm_ids + len(group)} of {total_osm_ids}")
        procedsed_osm_ids += len(group)
        # Prepare payload; adjust the key names if required by the API.
        osm_ids = [osm_data.get("osm_id") for osm_data in group]
        if not osm_ids:
            logger.warning("No OSM IDs found in the group.")
            continue
        # Make the API call to get location data
        osm_nodes = find_nodes_by_osm_ids(osm_ids,logger)
        if not osm_nodes:
            bad_osm_ids.extend(osm_ids)
            logger.warning(f"No nodes found for the provided OSM IDs. 'osm_ids': {', '.join(map(str, osm_ids))}")
            continue
        # Process the nodes to extract location data
        for req_item in group:
            node_osm_data = None
            for node in osm_nodes:
                 if node and 'osm_id' in node and str(node['osm_id']) == req_item.get("osm_id"):
                    node_osm_data = node
                    break
            if not node_osm_data:
                bad_osm_ids.append(req_item.get("osm_id"))
                logger.warning(f"No node found for OSM ID: {req_item.get('osm_id')}")
            else:
                req_item.update(node_osm_data)
                if not req_item.get("location"):
                    bad_osm_ids.append(req_item.get("osm_id"))
                    logger.warning(f"No location found for settlement with OSM ID: {req_item.get('osm_id')}")
        drop_bad_osm_ids(settlements, bad_osm_ids)
        save_settlements(settlements, group)
        step_end_time = time.time()
        logger.info(f"Processed {len(group)} OSM IDs in {step_end_time - step_start_time:.2f} seconds.")

def drop_bad_osm_ids(settlements, bad_osm_ids): 
    for bad_osm_id in bad_osm_ids:
        for settlement in settlements:
            if settlement.get("osm_id") == bad_osm_id or settlement.get("osm_id") == f"n{bad_osm_id}":
                logger.warning(f"Dropping settlement with bad OSM ID: {bad_osm_id}")
                settlement.pop("osm_id", None)
                break

# def get_location_from_osm(osm_id):
#     """Fetches location from Nominatim API by OSM ID."""
#     if not osm_id or not osm_id.isdigit():
#         return None

#     # OSM IDs can be for Nodes (N), Ways (W), or Relations (R).
#     # We try each prefix until we get a result.
#     for osm_type in ['N', 'W', 'R']:
#         url = f"https://nominatim.openstreetmap.org/lookup?osm_ids={osm_type}{osm_id}&format=json"
#         headers = {'User-Agent': 'UASettlementsBot/1.0 (dev.bnotezz@gmail.com)'}
#         try:
#             response = requests.get(url, headers=headers)
#             response.raise_for_status()
#             data = response.json()
#             if data:
#                 # lon, lat format
#                 return [float(data[0]['lon']), float(data[0]['lat'])]
#         except requests.RequestException as e:
#             logger.error(f"Error fetching OSM ID {osm_type}{osm_id}: {e}")
#             return None
#         finally:
#             # Nominatim's usage policy requires a delay of at least 1 second per request.
#             time.sleep(1)
#     return None

def save_settlements(settlements, updated_data):
     # Update the original settlements with the new location data
    need__to_update = False
    for settlement in settlements:
        osm_id = settlement.get("osm_id")
        if osm_id:
            # Find the corresponding location data
            location_data = next((data for data in updated_data if data["osm_id"] == osm_id or data["osm_id"] == f"n{osm_id}"), None)
            if location_data:
                for k,v in location_data.items():
                    if k != "katotth_id" and  k != "koatuu_id" and  k != "osm_id" and v is not None:
                        need__to_update = True
                        settlement[k] = v

    if not need__to_update:
        return
    data_file = os.path.join("assets", "data", "settlements.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(settlements, f, ensure_ascii=False, indent=2)

def get_osm_data():
    """Finds and adds location data for settlements based on osm_id."""
    data_file = os.path.join("assets", "data", "settlements.json")

    with open(data_file, 'r', encoding='utf-8') as f:
        settlements = json.load(f)

    update_settlements_locations(settlements)
    logger.info("Location data fetching complete.")

if __name__ == '__main__':
    get_osm_data()
