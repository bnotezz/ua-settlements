import json
import os
import time
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_settlements(settlements):
    data_file = os.path.join("assets", "data", "settlements.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(settlements, f, ensure_ascii=False, indent=2)

def get_communities_data():
    """
    Get communities data from decentralization.ua API.
    """
    endpoint = "https://decentralization.ua/graphql?query={communities{title,id,area_id,region_id,area_name,region_name,created,population,square,center,koatuu,katottg}}"
    try:
        response = requests.post(endpoint)
        if response.status_code != 200:
            logger.error(f"Failed to fetch communities data: {response.status_code} {response.text}")
            return []
    
        data = response.json()
        communities = data.get("data", {}).get("communities", [])
        if not communities:
            logger.warning("No communities found in the response.")
            return []
        
        # Process and return the communities data
        processed_communities = []
        for community in communities:
            processed_community = {
                "id": community.get("id"),
                "name": community.get("title"),
                "oblast_id": community.get("area_id"),
                "oblast_name": community.get("area_name"),
                "district_id": community.get("region_id"),
                "district_name": community.get("region_name"),
                "created": community.get("created"),
                "hromada_center": community.get("center"),
                "population": community.get("population"),
                "square": community.get("square"),
                "koatuu": community.get("koatuu"),
                "katotth": community.get("katottg"),
            }

            # Київ and Севастополь are special cases    
            if processed_community.get("katotth") =="UA80000000000093317":
               continue
            processed_communities.append(processed_community)
        
        return processed_communities
    except Exception as e:
        logger.error(f"Error processing communities data: {e}")
        return []
    
def get_regions_data():
    """
    Get regions data from decentralization.ua API.
    """
    endpoint = "https://decentralization.ua/graphql?query={regions{title,area_id,id,population,square}}"
    try:
        response = requests.post(endpoint)
        if response.status_code != 200:
            logger.error(f"Failed to fetch regions data: {response.status_code} {response.text}")
            return []
    
        data = response.json()
        regions = data.get("data", {}).get("regions", [])
        if not regions:
            logger.warning("No regions found in the response.")
            return []
        
        # Process and return the regions data
        processed_regions = []
        for region in regions:
            processed_region = {
                "id": region.get("id"),
                "oblast_id": region.get("area_id"),
                "name": region.get("title"),
                "population": region.get("population"),
                "square": region.get("square"),
            }
            processed_regions.append(processed_region)
        
        return processed_regions
    except Exception as e:
        logger.error(f"Error processing regions data: {e}")
        return []

def get_areas_data():
    """
    Get areas data from decentralization.ua API.
    """
    endpoint = "https://decentralization.ua/graphql?query={areas{title,id,square,population,local_community_count,percent_communities_from_area,sum_communities_square}}"
    try:
        response = requests.post(endpoint)
        if response.status_code != 200:
            logger.error(f"Failed to fetch areas data: {response.status_code} {response.text}")
            return []
    
        data = response.json()
        areas = data.get("data", {}).get("areas", [])
        if not areas:
            logger.warning("No areas found in the response.")
            return []
        
        # Process and return the areas data
        processed_regions = []
        for region in areas:
            processed_region = {
                "id": region.get("id"),
                "name": region.get("title"),
                "population": region.get("population"),
                "square": region.get("square"),
            }
            processed_regions.append(processed_region)
        
        return processed_regions
    except Exception as e:
        logger.error(f"Error processing areas data: {e}")
        return []

def update_settlements_data(settlements, communities_data,regions_data,areas_data):
    """
    Update settlements with communities data.
    """
    regions_to_update = dict()
    for settlement in settlements:
        for community in communities_data:
            if settlement.get("katotth_id") == community.get("katotth"):
                if(community.get("population")):
                    settlement["population"] = community.get("population")
                if(community.get("square")):
                    settlement["square"] = community.get("square")
                if(community.get("hromada_center")):
                    settlement["hromada_center"] = community.get("hromada_center")
                for region in regions_data:
                    if region.get("id") == community.get("district_id"):
                        regions_to_update[settlement["parent_katotth"]] = {"population": region.get("population"), "square": region.get("square")}
                        
                        for area in areas_data:
                            if area.get("id") == community.get("oblast_id"):
                                for rayon in settlements:
                                    if(settlement["parent_katotth"] == rayon.get("katotth_id")):
                                        regions_to_update[rayon.get("parent_katotth")] = {"population": area.get("population"), "square": area.get("square")}
                                        break
                                break
                        break
                break
    for k,v in regions_to_update.items():
        for settlement in settlements:
            if settlement.get("katotth_id") == k:
                if(v.get("population")):
                    settlement["population"] = v.get("population")
                if(v.get("square")):
                    settlement["square"] = v.get("square")

    save_settlements(settlements)
    logger.info("Decentralization data added to settlements.")

def get_community_map(id):
    """
    Get a community map by its ID.
    """
    endpoint = f"https://decentralization.ua/api/v1/communities/{id}/geo_json"
    try:
        response = requests.get(endpoint)
        if response.status_code != 200:
            logger.error(f"Failed to fetch community data: {response.status_code} {response.text}")
            return {}
    
        data = response.json()
        if not data or not data.get("geometry"):
            logger.warning(f"No community map found with ID: {id}")
        
        return data
    except Exception as e:
        logger.error(f"Error fetching community data: {e}")
        return {}

def update_communities_map(communities_data, settlements):
    """
    Create a map of communities by their KOATUU IDs.
    
    Args:
        communities_data (list): List of community dictionaries.
        settlements (list): List of settlement dictionaries.
    
    Returns:
        dict: A map of communities by their KOATUU IDs.
    """

    #if(comminities_map and comminities_map.get("features")):

    map_file = os.path.join("assets", "maps", "communities.geojson")
    
    with open(map_file, 'r', encoding='utf-8') as f:
        communities_map = json.load(f)
    if not communities_map:
        communities_map = {"type":"FeatureCollection", "features": []}
    map_features = communities_map.get("features", [])
    for settlement in settlements:
        koatth_id = settlement.get("katotth_id")
        for community in communities_data:
            if koatth_id and koatth_id == community.get("katotth"):
                community["parent_katotth"] = settlement.get("parent_katotth")
                break
    for community in communities_data:
        id = community.get("id")
        katotth = community.get("katotth")
        if id and katotth:
            community_map_feature = None
            for map_feature in map_features:
                if map_feature.get("properties", {}).get("katotth") == katotth:
                    community_map_feature =  map_feature
                    break
            if(not community_map_feature):
                community_map_feature = get_community_map(id)
                map_features.append(community_map_feature)
            community_map_feature.get("properties", {}).update(community)
            if(not community_map_feature.get("geometry")):
                logger.warning(f"Community {community.get('name')} with KOATUU ID {katotth} has no geometry data.")
                continue
            
    logger.info(f"Created communities map with {len(communities_map)} entries.")

    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump(communities_map, f, ensure_ascii=False, indent=2)
    logger.info(f"Communities map saved to {map_file}")

    return communities_map  

def update_district_maps(settlements):
    """
    Update district maps with communities data.
    
    Args:
        settlements (list): List of settlement dictionaries.
    
    Returns:
        None
    """
    try:
        map_file = os.path.join("assets", "maps", "districts.geojson")
        with open(map_file, 'r', encoding='utf-8') as f:
            districts_map = json.load(f)
        
        if not districts_map:
            logger.warning("No districts map found.")
            return
        if not districts_map.get("features"):
            logger.warning("No features found in the districts map.")
            return

        features = districts_map.get("features", [])

        for district in features:
            if(not district.get("properties")):
                logger.warning("District feature has no properties.")
                continue
            
            district_properties = district.get("properties", {})
            koatth_id = district_properties.get("katotth")
            if not koatth_id:
                logger.warning("District feature has no KOATUU ID.")
                continue

            for settlement in settlements:
                if settlement.get("katotth_id") == koatth_id:
                    district_properties["parent_katotth"] = settlement.get("parent_katotth")
                    district_properties["name"] = f"{settlement.get('name')} район"
                    if( settlement.get("population")):
                        district_properties["population"] = settlement.get("population")
                    if( settlement.get("square")):
                        district_properties["square"] = settlement.get("square")
                    break
    
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(districts_map, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Districts map saved to {map_file}")
    except Exception as e:
        logger.error(f"Error updating district maps: {e}")
        return

def add_decentralization_data():
    """
    Add decentralization data to settlements.
    """
    data_file = os.path.join("assets", "data", "settlements.json")

    with open(data_file, 'r', encoding='utf-8') as f:
        settlements = json.load(f)

    communities_data = get_communities_data()
    if not communities_data:
        logger.warning("No communities data found.")
        return
    areas_data = get_areas_data()
    if not areas_data:
        logger.warning("No areas data found.")
        return
    regions_data = get_regions_data()
    if not regions_data:
        logger.warning("No regions data found.")
        return
    # Update settlements with communities data
    update_settlements_data(settlements,communities_data,regions_data,areas_data)
    
    update_communities_map(communities_data,settlements)

    update_communities_features_by_prevmap(settlements)
    
    update_district_maps(settlements)

def update_communities_features_by_prevmap(settlements):
    map_file = os.path.join("assets", "maps", "communities.geojson")
    admin3_prev_map_file = os.path.join("assets", "maps", "old_maps","ua-2021","ADMIN_3.geojson")
    
    with open(map_file, 'r', encoding='utf-8') as f:
        communities_map = json.load(f)
    if not communities_map:
        communities_map = {"type":"FeatureCollection", "features": []}

    with open(admin3_prev_map_file, 'r', encoding='utf-8') as f:
        admin3_prev_map = json.load(f)
    if not admin3_prev_map:
        logger.error("No previous admin 3 map found.")
        return
    
    map_features = admin3_prev_map.get("features", [])
    if(not map_features):
        logger.error("No features found in the ADMIN 3 map.")
        return
    
    for feature in map_features:
        if(not feature.get("properties")):
            logger.warning("Feature has no properties.")
            continue
        
        katotth = feature.get("properties", {}).get("COD_3")
        if not katotth:
            logger.warning(f"Feature has no katotth ID.")
            continue

        community_instance = None
        for settlement in settlements:
            if settlement.get("katotth_id") == katotth:
                community_instance = settlement
                break

        if not community_instance:
            logger.warning(f"Settlement with katotth ID {katotth} not found in the settlements data.")
            continue
        
        community_map_feature = None
        for cmap_feature in communities_map.get("features", []):
            if cmap_feature.get("properties", {}).get("katotth") == katotth:
                community_map_feature =  cmap_feature
                break
        
        if(not community_map_feature):
            logger.warning(f"Community with katotth ID {katotth} not found in the communities map.")
            community_map_feature = {"type":"Feature", "properties": {}, "geometry": {}}
            communities_map.get("features", []).append(community_map_feature)
        
        if(not community_map_feature.get("geometry")):
            community_map_feature["geometry"] = feature.get("geometry", {})

        if(feature.get("properties")):
            oblast_name = feature.get("properties", {}).get("ADMIN_1")
            if oblast_name:
                community_map_feature.get("properties", {})["oblast_name"] = oblast_name
            region_name = feature.get("properties", {}).get("ADMIN_2")
            if region_name:
                community_map_feature.get("properties", {})["district_name"] = region_name
            type = feature.get("properties", {}).get("TYPE")
            if type:
                community_map_feature.get("properties", {})["type"] = type

        properties = {"katotth": katotth}
        if(community_instance.get("name")):
            properties["name"] = f"{community_instance.get("name")}  територіальна громада"
        
        if(community_instance.get("parent_katotth")):
            properties["parent_katotth"] = community_instance.get("parent_katotth")
        if(community_instance.get("koatuu_id")):
            properties["koatuu"] = community_instance.get("koatuu_id")

        community_map_feature.get("properties", {}).update(properties)

    # Save the updated community map feature
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump(communities_map, f, ensure_ascii=False, indent=2)
    logger.info(f"Communities map saved to {map_file}")

    # Save updated settlements data
    data_file = os.path.join("assets", "data", "settlements.json")
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(settlements, f, ensure_ascii=False, indent=2)
    logger.info(f"Settlements data saved to {data_file}")

if __name__ == '__main__':
    add_decentralization_data()
