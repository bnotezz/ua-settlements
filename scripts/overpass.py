import requests
import logging
import time

# Overpass API endpoint
url = "http://overpass-api.de/api/interpreter"

def find_nodes_by_osm_ids(osm_ids, logger, retries=2):
    """
    Find nodes by their OSM IDs using Overpass API.
    """
    # Ensure the list of IDs is not empty
    if not osm_ids:
        logger.warning("No OSM IDs provided.")
        return []
    
    # Build the query string; note the comma-separated list of IDs
    query = "[out:json];\nnode(id:{});\nout;".format(",".join(map(str, osm_ids)))
    try:
        # Make the request to Overpass API
        response = requests.get(url, params={'data': query}, timeout=60)  # Add a 60-second timeout
   
        if response.status_code == 200:
            data = response.json()
            return extract_entities_data(data['elements'])
        else:
            logger.error(f"Error fetching data for OSM IDs {osm_ids}: {response.status_code} {response.text}")
            if( retries > 0):
                logger.info(f"Retrying... {retries} attempts left.")
                time.sleep(2)
                return find_nodes_by_osm_ids(osm_ids, retries - 1)
            return []
    except requests.RequestException as e:
        logger.error(f"Error fetching data for OSM IDs {osm_ids}: {e}")
        if( retries > 0):
            logger.info(f"Retrying... {retries} attempts left.")
            time.sleep(2)
            return find_nodes_by_osm_ids(osm_ids, retries - 1)
        return []
    except Exception as e:
        logger.error(f"Error fetching data for OSM IDs {osm_ids}: {e}")
        if( retries > 0):
            logger.info(f"Retrying... {retries} attempts left.")
            time.sleep(2)
            return find_nodes_by_osm_ids(osm_ids, retries - 1)
        return []
    finally:
        # Be respectful of the API rate limits
        time.sleep(1)

# This function finds entities by a specific property and its values using Overpass API.
# It can be used to find nodes, ways, or relations based on the provided key and values.
# The logger is used to log any warnings or errors encountered during the process.
# The type parameter can be used to specify the type of entity to search for (e.g., "node" for nodes, "way" for ways, "relation" for relations).
## The function retries the request if it fails, up to a specified number of retries.
# It returns a list of entities that match the specified property and values.
def find_entities_by_propety(key, values, logger, type="node", retries=2):
    """
    Find entities by property value using Overpass API.
    """
    if not key:
        logger.warning("No Property Key provided.")
        return []
    if not values:
        logger.warning("No Property Values provided.")
        return []
    
    # Build the query string; note the comma-separated list of IDs
    qFiels = "\n".join(map(lambda v: f"{type}['{key}'='{v}'];", values))
    query = f"[out:json];\n(\n{qFiels}\n);\nout;"
    try:
        # Make the request to Overpass API
        response = requests.get(url, params={'data': query}, timeout=60)  # Add a 60-second timeout
    
        if response.status_code == 200:
            data = response.json()
            return extract_entities_data(data['elements'])
        else:
            logger.error(f"Error fetching data for {key}={values}: {response.status_code} {response.text}")
            if( retries > 0):
                logger.info(f"Retrying... {retries} attempts left.")
                time.sleep(2)
                return find_entities_by_propety(key,values,logger,type, retries - 1)
            return []
    except requests.RequestException as e:
        logger.error(f"Error fetching data for {key}={values}: {e}")
        if( retries > 0):
            logger.info(f"Retrying... {retries} attempts left.")
            time.sleep(2)
            return find_entities_by_propety(key,values,logger,type, retries - 1)
        return []
    # Catch any other exceptions that may occur
    except Exception as e:
        logger.error(f"Error fetching data for {key}={values}: {e}")
        if( retries > 0):
            logger.info(f"Retrying... {retries} attempts left.")
            time.sleep(2)
            return find_entities_by_propety(key,values,logger,type, retries - 1)
        return []
    finally:
        # Be respectful of the API rate limits
        time.sleep(1)

def extract_entities_data(entities):
    """
    Extract relevant data from entities.
    """
    extracted_data = []
    for entity in entities:
        type = entity.get("type", None)
        id = entity.get("id", None)
        osm_data = {}

        if(type == "node"):
            osm_data["osm_id"] = f"{id}"
        elif( type == "way"):
            osm_data["osm_id"] = f"w{id}"
        elif( type == "relation"): 
            osm_data["osm_id"] = f"r{id}"

        if 'lat' in entity and 'lon' in entity:
            osm_data["location"] = [entity['lon'], entity['lat']]

        if 'tags' in entity:
            # Extract additional tags if available
            if entity['tags'].get('old_name'):
                osm_data["old_name"] = entity['tags']['old_name']
            if entity['tags'].get('postal_code'):
                osm_data["postal_code"] = entity['tags']['postal_code']
            if entity['tags'].get('wikidata'):
                osm_data["wikidata"] = entity['tags']['wikidata']
            if entity['tags'].get('wikipedia'):
                wikipedia = entity['tags']['wikipedia']
                if( wikipedia.startswith("uk:")):
                    osm_data["wikipedia"] = wikipedia
            if entity['tags'].get('wikipedia:uk'):
                osm_data["wikipedia"] = entity['tags']['wikipedia:uk']
            if entity['tags'].get('population'):
                osm_data["population"] = entity['tags']['population']
            if entity['tags'].get('katotth'):
                osm_data["katotth_id"] = entity['tags']['katotth']
            if entity['tags'].get('name:en'):
                osm_data["name:en"] = entity['tags']['name:en']
            if entity['tags'].get('name:ru'):
                osm_data["name:ru"] = entity['tags']['name:ru']
            if entity['tags'].get('name:pl'):
                osm_data["name:pl"] = entity['tags']['name:pl']
        extracted_data.append(osm_data)
    return extracted_data