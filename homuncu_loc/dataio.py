import fnmatch
import os

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
