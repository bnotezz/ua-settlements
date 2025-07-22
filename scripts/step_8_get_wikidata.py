import json
import os
import time
import requests
import logging
from categories import is_area_type

qury_endpoint_url = "https://query.wikidata.org/sparql"
sparql_headers = {'User-Agent': 'UASettlementsBot/1.0'}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chunk_list(data, chunk_size):
    """Yield successive chunks of size chunk_size from data."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def query_wikidata(query, retries=2):
    """Executes a SPARQL query against the Wikidata endpoint."""
    try:
        response = requests.get(qury_endpoint_url, headers=sparql_headers, params={'query': query, 'format': 'json'},timeout=60)  # Add a 60-second timeout
        response.raise_for_status()
        data = response.json()
    
        results = data.get('results', {}).get('bindings', [])

        return results
    except requests.RequestException as e:
        if retries > 0:
            logger.warning(f"Error querying Wikidata: {e}. Retrying... {retries} attempts left.")
            time.sleep(2)
            return query_wikidata(query, retries - 1)
        logger.error(f"Error querying Wikidata: {e}")
        return None
    finally:
        # Be respectful of the API rate limits
        time.sleep(1)

def get_wikidata_details(wikidata_ids,retries=2):
    """Fetches the sitelink URL for a given Wikidata ID and site key."""
    if not wikidata_ids:
        return None
    endpoint =f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={"|".join(wikidata_ids)}&format=json"
    try:
        response = requests.get(endpoint, headers=sparql_headers, timeout=60)  # Add a 60-second timeout
        response.raise_for_status()
        data = response.json()
        entities = data.get('entities', {})
        if entities:
            return entities
        else:
            logger.warning(f"No entity found for Wikidata ID {",".join(wikidata_ids)}")
            return None
    except Exception as e:
        if retries > 0:
            logger.warning(f"Error fetching details for {",".join(wikidata_ids)} : {e}. Retrying... {retries} attempts left.")
            time.sleep(2)
            return get_wikidata_details(wikidata_ids, retries - 1)
        else:
         logger.error(f"Error fetching details for {",".join(wikidata_ids)}: {e}")
         return None

def get_wikidata_id(prop, value):
    """Fetches a Wikidata entity ID based on a property and its value."""
    if not value:
        return None

    query = f"""
    SELECT ?item WHERE {{
      ?item wdt:{prop} "{value}".
    }}
    LIMIT 3
    """
    results = query_wikidata(query)
    if results:
        if(len(results) > 1):
            print(f"Warning: Multiple wikidata results found for {prop}={value}. Using the first one.")
        wikidata_url = results[0]['item']['value']
        return wikidata_url.split('/')[-1] # Extract the Q-ID
    else:
        logger.warning(f"No Wikidata ID found for {prop}={value}")
        return None

def find_wikidata_id_by_koatuu(settlements):
    """Finds the Wikidata ID for a settlement by its KOATUU ID."""
    existing_wikidata_ids = {settlement.get("wikidata") for settlement in settlements if settlement.get("wikidata")}
    for settlement in settlements:
        wikidata_id = settlement.get("wikidata")
        
        if(not wikidata_id):
            koatuu_id = settlement.get("koatuu_id")
            if koatuu_id:
                query = f"""
                        SELECT 
                        (STRAFTER(STR(?item), "entity/")    AS ?itemID) 
                        (STRAFTER(STR(?instanceOf), "entity/") AS ?P31_ID)
                        ?itemLabel
                        ?instanceOfLabel
                        WHERE {{
                        ?item wdt:P1077 "{koatuu_id}".
                        ?item wdt:P31  ?instanceOf .
                        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "uk".  }}
                        }}
                        LIMIT 3
                        """
                results = query_wikidata(query)
                if results:
                    for result in results:
                        wikidata_id = result['itemID']['value']
                        instance_of = result['P31_ID']['value']

                        if instance_of in ["Q4414033","Q104841013","Q21683299","Q21683299","Q634099","Q27002"]:#hromada
                            if not settlement.get("category") == "H":
                                wikidata_id = None
                                continue
                        elif instance_of in ["Q2514025","Q21672098","Q4100864","Q15078955","Q486972"]:#village
                            if not settlement.get("category") in ["C","X"]:
                                wikidata_id = None
                                continue
                        elif instance_of == "Q1267632":#rayon
                             if not settlement.get("category") in ["P"]:
                                wikidata_id = None
                                continue
                        elif instance_of =="Q3348196":#oblast
                            if not settlement.get("category") in ["O"]:
                                wikidata_id = None
                                continue

                        elif instance_of in ["Q5123999","Q12131624","Q7930989"]:#city
                            if not settlement.get("category") in ["M","K"]:
                                wikidata_id = None
                                continue
                        else:
                            logger.warning(f"Unknown instance of {instance_of} for settlement {settlement.get('name')}, skipping")
                            wikidata_id = None
                            continue

                        if(wikidata_id):
                            break
                
                if wikidata_id:
                    logger.info(f"Found Wikidata ID for {settlement['name']} by KOATUU ID: {wikidata_id}")
                if wikidata_id and wikidata_id not in existing_wikidata_ids:
                    existing_wikidata_ids.add(wikidata_id)
                    settlement["wikidata"] = wikidata_id
                elif wikidata_id:
                    logger.info(f"Wikidata ID {wikidata_id} already occurs in other settlement, skipping")
                    wikidata_id = None


def find_wikidata_ids(settlements):
    """Finds and adds Wikidata entity IDs for settlements."""
    if( not settlements or not isinstance(settlements, list)):
        logger.warning("No settlements provided or settlements is not a list.")
        return
    
    existing_wikidata_ids = {settlement.get("wikidata") for settlement in settlements if settlement.get("wikidata")}

    for settlement in settlements:
        wikidata_id = settlement.get("wikidata")
        
        if(not wikidata_id):
             # Prioritize KATOTTH ID (P9435)
            wikidata_id = get_wikidata_id("P9435", settlement.get("katotth_id"))

            if wikidata_id:
                logger.info(f"Found Wikidata ID for {settlement['name']}: {wikidata_id}")

            if wikidata_id and wikidata_id not in existing_wikidata_ids:
                existing_wikidata_ids.add(wikidata_id)
                settlement["wikidata"] = wikidata_id
            elif wikidata_id:
                logger.info(f"Wikidata ID {wikidata_id} already occurs in other settlement, skipping")
                wikidata_id = None

def get_missing_data(settlements):
    """Finds and adds missing data for settlements."""  
    if( not settlements or not isinstance(settlements, list)):
        logger.warning("No settlements provided or settlements is not a list.")
        return
    
    logger.info("Finding missing data from wikidata for settlements...")

    existing_wikidata_ids = [
        settlement.get("wikidata")
        for settlement in settlements
        if settlement.get("wikidata") and (
            not settlement.get("location")
            or not settlement.get("osm_id")
            or not settlement.get("postal_code")
            or not settlement.get("wikipedia")
            or not settlement.get("name:pl")
        )
    ]

    wikidata_to_update = dict()
    procedsed_wikidata_ids = 0
    total_records_to_process = len(existing_wikidata_ids)
    for group in chunk_list(existing_wikidata_ids, 15):
    
        entities = get_wikidata_details(group)

        if not entities:
            logger.warning(f"No entities found for Wikidata IDs: {', '.join(group)}")
            continue
        for wikidata_id, entity in entities.items():
            data_to_update = {}

            wikipedia = entity.get('sitelinks', {}).get('ukwiki', {}).get('title')
            if wikipedia:
                data_to_update["wikipedia"] = f"uk:{wikipedia}"

            coords = entity.get('claims', {}).get('P625', [])
            if coords:
                coord_value = coords[0].get('mainsnak', {}).get('datavalue', {}).get('value', {})
                if coord_value:
                    lon = coord_value.get('longitude')
                    lat = coord_value.get('latitude')
                    if lon is not None and lat is not None:
                        data_to_update["location"] = [lon, lat]

            postal_code = entity.get('claims', {}).get('P281', [])
            if postal_code:
                postal_code_value = postal_code[0].get('mainsnak', {}).get('datavalue', {}).get('value')
                if postal_code_value:
                    data_to_update["postal_code"] = postal_code_value

            en_name = entity.get('labels', {}).get('en', {}).get('value')
            if en_name:
                data_to_update["name:en"] = en_name

            ru_name = entity.get('labels', {}).get('ru', {}).get('value')
            if ru_name:
                data_to_update["name:ru"] = ru_name

            pl_name = entity.get('labels', {}).get('pl', {}).get('value')
            if pl_name:
                data_to_update["name:pl"] = pl_name

            osm_id = entity.get('claims', {}).get('P402', [])
            if osm_id:
                osm_id_value = osm_id[0].get('mainsnak', {}).get('datavalue', {}).get('value')
                if osm_id_value:
                    if osm_id_value.startswith("r"):
                        data_to_update["osm_id"] = osm_id_value
                    else:
                        data_to_update["osm_id"] = f"r{osm_id_value}"


            if data_to_update:
                wikidata_to_update[wikidata_id] = data_to_update
                #logger.info(f"Found missing data for Wikidata ID {wikidata_id}: {data_to_update}")
            
        procedsed_wikidata_ids += len(group)
        logger.info(f"Processed Wikidata IDs {procedsed_wikidata_ids } of {total_records_to_process}")
           
    
    for settlement in settlements:
        wikidata_id = settlement.get("wikidata")
        if wikidata_id and wikidata_id in wikidata_to_update:
            data_to_update = wikidata_to_update[wikidata_id]
            for key, value in data_to_update.items():
                if value and not settlement.get(key):
                    if( key == "osm_id" and value.startswith("r") and not is_area_type(settlement)):
                       continue
                    settlement[key] = value
                    logger.info(f"Updated {key} for settlement {settlement.get('name')} with Wikidata ID {wikidata_id}: {value}")

def get_wikidata():
   
    data_file = os.path.join("assets", "data", "settlements.json")

    with open(data_file, 'r', encoding='utf-8') as f:
        settlements = json.load(f)

    find_wikidata_ids(settlements)
    find_wikidata_id_by_koatuu(settlements)

    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(settlements, f, ensure_ascii=False, indent=2)

    logger.info("Saved settlements with Wikidata IDs.")

    get_missing_data(settlements)
  
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(settlements, f, ensure_ascii=False, indent=2)

    logger.info("Saved settlements with missing data from Wikidata.")

if __name__ == '__main__':
    get_wikidata()
    logger.info("Wikidata ID fetching complete.")