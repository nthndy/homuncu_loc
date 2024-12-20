import fnmatch
import os
import pandas as pd
from collections import defaultdict
from glob import glob
import gspread
import pandas as pd
import btrack
import shutil

def try_load_nemo_h5(sc_fn, return_options=['tracks', 'masks']):
    """
    Attempts to load single-cell analysis data (tracks and/or masks) from an HDF5 file.

    This function tries to open an HDF5 file specified by `sc_fn` to extract single-cell analysis data.
    The data can include 'tracks', 'masks', or both, based on the `return_options` parameter.
    If the file cannot be accessed from its original location, the function attempts to copy it to a local directory and access it from there.

    Parameters:
    sc_fn (str): Path to the HDF5 file containing single-cell analysis data.
    return_options (list of str, optional): A list specifying the types of data to return.
        Options include 'tracks', 'masks', or both. Defaults to ['tracks', 'masks'].

    Returns:
    tuple: A tuple containing the requested data. Each element of the tuple corresponds to one of the `return_options`.
        Returns (None, None) if neither tracks nor masks can be loaded due to errors.

    Raises:
    Exception: Propagates any exceptions encountered during file loading or copying.

    Notes:
    - If an error occurs while loading the file from its original location, the function will attempt to copy the file to './temp_sc_dir' and load it from there.
    - If the file cannot be loaded even from the local copy, the function prints an error message and returns (None, None).

    Example usage:
    tracks, masks = try_load_nemo_h5('/path/to/file.h5', return_options=['tracks', 'masks'])
    """

    masks = None  # Initialize masks variable as None
    tracks = None  # Initialize tracks variable as None

    try:
        with btrack.io.HDF5FileHandler(sc_fn, 'r', obj_type='obj_type_1') as reader:
            if 'masks' in return_options:
                masks = reader.segmentation  # Assign segmentation masks data to masks variable
            if 'tracks' in return_options:
                tracks = reader.tracks  # Assign tracks data to tracks variable

    except Exception as e:  # Catch any exceptions during file opening
        print(f"Failed to load from server location: {e}. Attempting to copy file locally.")

        temp_sc_dir = './temp_sc_dir' # Define name of temporary local directory
        os.makedirs(temp_sc_dir, exist_ok=True)  # Create temporary directory if it doesn't exist
        local_sc_fn = os.path.join(temp_sc_dir, os.path.basename(sc_fn))  # Define local file path
        shutil.copy(sc_fn, local_sc_fn)  # Copy file from server location to local directory
        print(f"Copied {sc_fn} to {local_sc_fn}")  # Print success message

        try:
            with btrack.io.HDF5FileHandler(local_sc_fn, 'r', obj_type='obj_type_1') as reader:
                if 'masks' in return_options:
                    masks = reader.segmentation  # Assign segmentation masks data to masks variable
                if 'tracks' in return_options:
                    tracks = reader.tracks  # Assign tracks data to tracks variable
            print("Loaded file from local copy successfully.")  # Print success message
        except Exception as e:
            print(f"Failed to load file from local copy: {e}")
            return None, None  # Return None, None indicating both masks and tracks are not available

    # Return based on the specified options
    return_values = []
    if 'tracks' in return_options:
        return_values.append(tracks)  # Append tracks to return_values list
    if 'masks' in return_options:
        return_values.append(masks)  # Append masks to return_values list

    return tuple(return_values)  # Return return_values as a tuple


def load_expt_dir():
    """
    Load experiment data from a Google Sheets document.

    Returns:
        pd.DataFrame: A dataframe containing the data from the Google Sheet.
    """
    # Define the path to the credentials JSON file
    credentials_path = '/home/dayn/analysis/homuncu_loc/homuncu_loc/homunc_dir.json'

    # Define the title of the Google Spreadsheet
    spreadsheet_title = 'homunculoc_expt_directory'

    # Define the title of the worksheet
    worksheet_title = 'main'

    try:
        # Load the credentials
        gc = gspread.service_account(filename=credentials_path)

        # Open the Google Spreadsheet using its title
        spreadsheet = gc.open(spreadsheet_title)

        # Select the worksheet by title
        worksheet = spreadsheet.worksheet(worksheet_title)

        # Get all values from the worksheet
        data = worksheet.get_all_values()

        # Check if data is empty
        if not data:
            print("The worksheet is empty.")
            return pd.DataFrame()

        # Convert the data to a pandas dataframe
        df = pd.DataFrame(data, columns=data[0]).iloc[1:]

        return df

    except gspread.SpreadsheetNotFound:
        print(f"Spreadsheet with title '{spreadsheet_title}' not found.")
        return pd.DataFrame()

    except gspread.WorksheetNotFound:
        print(f"Worksheet with title '{worksheet_title}' not found in spreadsheet '{spreadsheet_title}'.")
        return pd.DataFrame()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return pd.DataFrame()


def find_h5_files(root_dir):
    """
    Recursively searches for files with the '.h5' extension within the specified directory.

    Args:
        root_dir (str): The directory path to start searching for '.h5' files.

    Returns:
        list: A list of file paths that match the '.h5' extension.
    """
    matches = []
    for root, dirnames, filenames in os.walk(root_dir):
        for filename in fnmatch.filter(filenames, '*.h5'):
            matches.append(os.path.join(root, filename))
    return matches


def find_files_with_basename(target_basename, start_dir='.'):
    """
    Searches for files within the specified directory that have the given target basename.

    Args:
        target_basename (str): The target base filename to search for.
        start_dir (str, optional): The directory path to start searching for files. Default is the current directory.

    Returns:
        list: A list of file paths that have the same basename as the target_basename.
    """
    matching_files = []

    for dirpath, dirnames, filenames in os.walk(start_dir):
        for fname in filenames:
            if os.path.basename(fname) == target_basename:
                full_path = os.path.join(dirpath, fname)
                matching_files.append(full_path)

    return matching_files


def create_experiment_structure(base_dir):
    """
    Creates a directory structure for an experiment based on cell types and markers.

    Parameters:
    - base_dir (str): The root directory where the experiment directories will be created.

    Directory Structure:
    - For cell types with 'macrophage' in the name:
        - Two subdirectories are created: 'Infected' and 'Uninfected'
        - Under these, folders named according to the last two markers in the `markers` list are created.
    - For all other cell types:
        - Directories named according to the first two markers in the `markers` list are created.

    Example:
    If base_dir is '/path/to/experiment', the structure would be:
    /path/to/experiment/
        iAT1_iAT2_experiments/
            DAPI_SPC_PDPN_ZO1/
            DAPI_NKX21_PDPN_ZO1/
        iAT1_iAT2_iVEC_macrophage_experiments/
            Infected/
                DAPI_ZO1_MTB_CDX/
                DAPI_ZO1_CD16_MTB/
            Uninfected/
                DAPI_ZO1_MTB_CDX/
                DAPI_ZO1_CD16_MTB/
        other_experiments/
            DAPI_SPC_PDPN_ZO1/
            DAPI_NKX21_PDPN_ZO1/
    """

    # Define the cell types for which directory structure should be created
    cell_types = [
        "iAT1_iAT2_experiments",
        "iAT1_iAT2_iVEC_macrophage_experiments",
        "other_experiments"
    ]

    # Define the marker labels
    markers = [
        "DAPI_SPC_PDPN_ZO1",
        "DAPI_NKX21_PDPN_ZO1",
        "DAPI_ZO1_MTB_CDX",
        "DAPI_ZO1_CD16_MTB"
    ]

    # Loop through each cell type to create directories
    for cell_type in cell_types:
        cell_type_dir = os.path.join(base_dir, cell_type)
        os.makedirs(cell_type_dir, exist_ok=True)

        # If the cell type contains the word 'macrophage', create 'Infected' and 'Uninfected' subdirs
        if "macrophage" in cell_type:
            macrophage_subdirs = ["Infected", "Uninfected"]
            for subdir in macrophage_subdirs:
                subdir_path = os.path.join(cell_type_dir, subdir)
                os.makedirs(subdir_path, exist_ok=True)

                # Create directories for the last two markers
                for marker in markers[2:]:
                    marker_subdir = os.path.join(subdir_path, marker)
                    os.makedirs(marker_subdir, exist_ok=True)
        else:
            # For all other cell types, create directories for the first two markers
            for marker in markers[:2]:
                marker_subdir = os.path.join(cell_type_dir, marker)
                os.makedirs(marker_subdir, exist_ok=True)


def compare_directories_recursive(dir1, dir2):
    """
    Compares the contents of two directories recursively and returns the files in each directory and those missing in the second directory.

    Parameters:
    - dir1 (str): Path to the first directory.
    - dir2 (str): Path to the second directory.

    Returns:
    - tuple: A tuple containing three lists:
        1. List of all files in `dir1`.
        2. List of all files in `dir2`.
        3. List of files that are present in `dir1` but missing in `dir2`.

    Note:
    Only file names are compared. Directory paths and file contents are not considered in the comparison.

    Example:
    If dir1 contains "a.txt" and dir2 contains "b.txt", the function will return:
    (["/path/to/dir1/a.txt"], ["/path/to/dir2/b.txt"], ["/path/to/dir1/a.txt"])
    """

    # Get a list of all files in dir1 and its subdirectories
    files_in_dir1 = [os.path.join(root, file) for root, dirs, files in os.walk(dir1) for file in files]

    # Get a list of all files in dir2 and its subdirectories
    files_in_dir2 = [os.path.join(root, file) for root, dirs, files in os.walk(dir2) for file in files]

    # Find files in dir1 that are not in dir2. Comparison is based on file names only.
    missing_files = [file for file in files_in_dir1 if os.path.basename(file) not in [os.path.basename(file) for file in files_in_dir2]]

    return files_in_dir1, files_in_dir2, missing_files


def find_empty_files(directory):
    """
    Traverse a directory recursively to find all empty files.

    Parameters:
    - directory (str): The path to the directory to search.

    Returns:
    - list: A list containing the paths of all empty files found in the directory and its subdirectories.

    Example:
    If the directory contains files "a.txt" (empty) and "b.txt" (non-empty), the function will return:
    ["/path/to/directory/a.txt"]

    Note:
    The function considers a file to be empty if its size is 0 bytes.
    """

    # List to store the paths of empty files
    empty_files = []

    # Traverse the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            # Check if the file size is 0 bytes
            if os.path.getsize(file_path) == 0:
                empty_files.append(file_path)

    return empty_files


def sc_analysis_progress_check(root_dir):
    """
    ... (Keeping the docstring same as before)
    """
    results = []
    IDs = []
    id_counts = defaultdict(int)

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.vsi'):
                vsi_path = os.path.join(root, file)
                vsi_basename = os.path.splitext(file)[0]
                vsi_ID = vsi_basename.split('_')[-1]

                # Modify the ID if it's already been encountered
                id_counts[vsi_ID] += 1
                if id_counts[vsi_ID] > 1:
                    suffix = chr(96 + id_counts[vsi_ID])
                    vsi_ID = f"{vsi_ID}.{suffix}"

                # Check if the .vsi file exists and is not empty
                vsi_exists = os.path.exists(vsi_path) and os.path.getsize(vsi_path) != 0

                # Check for corresponding metadata directory
                metadata_dir = os.path.join(root, '_'+vsi_basename+'_')
                metadata_file_path = os.path.join(metadata_dir, 'stack1', 'frame_t_0.ets')
                metadata_exists = os.path.exists(metadata_file_path) and os.path.getsize(metadata_file_path) != 0

                # Check for corresponding .tif file
                tif_file_path = os.path.join(root, vsi_basename + '.tif')
                tif_exists = os.path.exists(tif_file_path) and os.path.getsize(tif_file_path) != 0

                # Check for corresponding sc directory
                sc_paths = glob(vsi_path.replace('images', 'sc_analyses').replace('.vsi', '*'))
                N_sc_files = len(sc_paths)
                type_sc = [fn.split(vsi_basename)[-1] for fn in sc_paths]

                # Determine the type of experiment
                expt_type = 'iAT1_iAT2' if 'iAT1_iAT2_experiments' in vsi_path else 'macroph_iAT1_iAT2'

                results.append({
                    "ID": int(vsi_ID),
                    "expt_type": expt_type,
                    "has_sc_analyses": False if N_sc_files < 1 else N_sc_files ,
                    "sc_types": False if len(type_sc) < 1 else type_sc,
                    "has_tif": tif_exists,
                    "has_vsi": vsi_exists,
                    "has_metadata": metadata_exists,
                    "image_location": root,# if tif_exists else None,  # Changed this to match the logic
                    "image_fn": vsi_basename,
                })

    return pd.DataFrame(data=results).sort_values(by='ID', ignore_index=True)


def ID_extractor(image_fn):
    """
    Extracts the ID from the provided image filename.

    The function assumes specific naming conventions. If the filename ends with
    'iat1.h5', 'iat2.h5', or 'mphi.h5', it extracts the second-to-last part of
    the basename after splitting on underscores. Otherwise, it extracts the last
    part of the basename.

    Parameters:
    - image_fn (str): The image filename from which the ID should be extracted.

    Returns:
    - str: Extracted ID from the image filename.
    """
    basename = os.path.splitext(image_fn)[0]
    if basename.endswith('iat1.h5') or basename.endswith('iat2.h5') or basename.endswith('mphi.h5'):
        ID = basename.split('_')[-2]
    else:
        ID = basename.split('_')[-1]
    return ID


def find_image_directory(top_dir, image_base_name):
    """
    Searches for the directory containing the specified image name within the top directory and its subdirectories.

    Parameters:
    - top_dir (str): The top-most directory where the search should begin.
    - image_base_name (str): The name of the image file to search for.

    Returns:
    - str or None: The directory path where the image was found. If the image is not found, returns None.
    """
    for dirpath, dirnames, filenames in os.walk(top_dir):
        if image_base_name in filenames:
            return dirpath
    return None
