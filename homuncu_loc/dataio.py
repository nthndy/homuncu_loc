import fnmatch
import os
import pandas as pd
from collections import defaultdict
from glob import glob


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
    Analyze the structure and accompanying files for images in a specified directory.

    Args:
    - root_dir (str): Root directory to start the search for .tif images.

    Returns:
    - pd.DataFrame: DataFrame containing information on each .tif file found in the root_dir and its subdirectories.

    The returned DataFrame includes:
    - ID: Modified identifier for the .tif file.
    - expt_type: Type of experiment either 'iAT1_iAT2' or 'macroph_iAT1_iAT2'.
    - has_sc_analyses: Number of sc analysis files associated with the image.
    - sc_types: Types of sc analyses associated with the image.
    - has_tif: Boolean indicating if the .tif file exists and is not empty.
    - has_vsi: Boolean indicating if the corresponding .vsi file exists and is not empty.
    - has_metadata: Boolean indicating if metadata for the image exists and is not empty.
    - image_location: Full path to the .tif file.
    - image_fn: Filename of the .tif image without the extension.
    """

    results = []
    IDs = []
    id_counts = defaultdict(int)

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.tif'):
                tif_path = os.path.join(root, file)
                tif_basename = os.path.splitext(file)[0]
                tif_ID = tif_basename.split('_')[-1].split('.tif')[0]

                # Modify the ID if it's already been encountered
                id_counts[tif_ID] += 1
                if id_counts[tif_ID] > 1:
                    suffix = chr(96 + id_counts[tif_ID])
                    tif_ID = f"{tif_ID}.{suffix}"

                # Check if the .tif file exists and is not empty
                tif_exists = os.path.exists(tif_path) and os.path.getsize(tif_path) != 0

                # Check for corresponding .vsi file
                vsi_file_path = os.path.join(root, tif_basename + '.vsi')
                vsi_exists = os.path.exists(vsi_file_path) and os.path.getsize(vsi_file_path) != 0

                # Check for corresponding metadata directory
                metadata_dir = os.path.join(root, '_'+tif_basename+'_')
                metadata_file_path = os.path.join(metadata_dir, 'stack1', 'frame_t_0.ets')
                metadata_exists = os.path.exists(metadata_file_path) and os.path.getsize(metadata_file_path) != 0

                # Check for corresponding sc directory
                sc_paths = glob(tif_path.replace('images', 'sc_analyses').replace('.tif','*'))
                N_sc_files = len(sc_paths)
                type_sc = [fn.split(tif_basename)[-1] for fn in sc_paths]

                # Determine the type of experiment
                expt_type = 'iAT1_iAT2' if 'iAT1_iAT2_experiments' in tif_path else 'macroph_iAT1_iAT2'

                results.append({
                    "ID": int(tif_ID),
                    "expt_type": expt_type,
                    "has_sc_analyses": False if N_sc_files < 1 else N_sc_files ,
                    "sc_types": False if len(type_sc) < 1 else type_sc,
                    "has_tif": tif_exists,
                    "has_vsi": vsi_exists,
                    "has_metadata": metadata_exists,
                    "image_location": tif_path,
                    "image_fn": tif_basename,
                })

    return pd.DataFrame(data=results).sort_values(by='ID', ignore_index=True)
