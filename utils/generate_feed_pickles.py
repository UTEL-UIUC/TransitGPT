import os
import sys
import warnings
import _pickle as cPickle
import gzip
import json
from pathlib import Path

warnings.filterwarnings("ignore")

# Get the directory of the current script
current_dir = Path(__file__).parent.resolve()

# Add the parent directory to sys.path
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))
from utils.constants import file_mapping
from gtfs_agent.gtfs_loader import GTFSLoader


def process_single_feed(agency_name, agency_data, output_directory, parent_dir):
    """
    Process a single GTFS feed: create GTFSLoader, pickle it, and update agency data.
    
    Args:
        agency_name (str): Name of the transit agency
        agency_data (dict): Dictionary containing agency's GTFS data information
        output_directory (str): Directory to store the pickled GTFSLoader
        parent_dir (Path): Parent directory path for relative path calculations
    
    Returns:
        dict: Updated agency_data dictionary
    """
    try:
        # if distance_unit is not ["m", "km", "ft", "mi"] set it to `m`
        if agency_data["distance_unit"] not in ["m", "km", "ft", "mi"]:
            agency_data["distance_unit"] = "m"
        
        # Create GTFSLoader object
        loader = GTFSLoader(
            gtfs=agency_name,
            gtfs_path=agency_data["file_loc"],
            distance_unit=agency_data["distance_unit"] or "km",  # Default to 'km' if None
        )

        # Load all tables
        loader.load_all_tables()

        # Create a filename based on the agency name
        filename = f"{agency_name}_gtfs_loader.pkl"
        filepath = os.path.join(output_directory, filename)

        # Pickle and save the loader
        with gzip.open(filepath, "wb") as f:
            cPickle.dump(loader, f)

        print(f"Pickled and stored {agency_name} at {filepath}")

        # Add relative pickle location to agency_data
        agency_data["pickle_loc"] = os.path.relpath(filepath, start=parent_dir).replace("\\", "/")
        
    except Exception as e:
        print(f"Error processing {agency_name}: {str(e)}")
        # Add error information to agency_data
        agency_data["error"] = str(e)
    
    return agency_data

def pickle_gtfs_loaders(file_mapping, output_directory, mapping_file_path):
    """
    Create, pickle, and store GTFSLoader objects based on the provided file mapping.
    Update the file_mapping with pickle locations and save it to a specified path.
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for agency_name, agency_data in file_mapping.items():
        print("<====Processing", agency_name, "====>")
        file_mapping[agency_name] = process_single_feed(
            agency_name, 
            agency_data, 
            output_directory, 
            parent_dir
        )

    # Save updated file_mapping
    with open(mapping_file_path, "w") as f:
        json.dump(file_mapping, f, indent=2)

    print(f"Updated file mapping saved to {mapping_file_path}")

if __name__ == "__main__":
    pickle_gtfs_loaders(
        file_mapping,
        os.path.join(parent_dir, "gtfs_data", "feed_pickles"),
        os.path.join(parent_dir, "gtfs_data", "file_mapping.json"),
    )
