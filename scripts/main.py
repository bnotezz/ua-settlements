import os
import time
import json
import logging
from step_1_generate_settlements import generate_settlements
from step_2_map_koatuu import map_koatuu
from step_3_add_osm_postal import add_osm_postal
from step_4_get_osm_data import get_osm_data
from step_5_find_regions_osm_data import find_regions_osm_data
from step_6_find_settlements_missing_osm_data import find_settlements_missing_osm_data
from step_7_add_decentralization_data import add_decentralization_data
from step_8_get_wikidata import get_wikidata

from data_validation import check_generated_data


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main function to run all data generation steps."""
    start_time = time.time()

    # Ensure output directory exists
    os.makedirs("assets/data", exist_ok=True)

    steps = {
        #"Step 1: Generating base settlements.json from KATOТTH": generate_settlements,
        #"Step 2: Mapping KOATUU IDs": map_koatuu,
       # "Step 3: Adding OSM_ID and Postal Code data": add_osm_postal,
        #"Step 4: Getting location and other data from OSM": get_osm_data,
        #"Step 5: Getting OSM data for regions": find_regions_osm_data,
        "Step 6: Getting missing OSM data for settlements": find_settlements_missing_osm_data,
        #"Step 7: Add decentralization data for settlements": add_decentralization_data,
        #"Step 8: Getting Wikidata IDs": get_wikidata,
    }

    for description, step_function in steps.items():
        logger.info(f"{description}...")
        step_start_time = time.time()
        try:
            step_function()
            step_end_time = time.time()
            logger.info(f"{description} complete. Took {step_end_time - step_start_time:.2f} seconds.")
        except Exception as e:
            logger.error(f"An error occurred during '{description}': {e}")
            break # Stop execution if a step fails

    end_time = time.time()
    logger.info(f"\nTotal project execution time: {end_time - start_time:.2f} seconds.")

    check_generated_data()

if __name__ == "__main__":
    main()