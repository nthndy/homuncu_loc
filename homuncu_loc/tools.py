from tqdm.auto import tqdm
import numpy as np
from skimage.morphology import binary_erosion, label
import numpy as np
from skimage.measure import regionprops

class ImageDimensionError(Exception):
    def __init__(self, expected_dimensionality, received_dimensionality):
        message = f"Invalid image dimensionality. Expected {expected_dimensionality}-dimensional image, but received {received_dimensionality}-dimensional image."
        super().__init__(message)


def remove_small_segments(mask_stack, threshold_size=1000):
    """
    Remove small segments from a stack of binary masks.

    This function iterates over a stack of binary masks (mask_stack) representing segmented objects and removes
    small segments whose total area is less than the specified threshold_size.

    Parameters:
        mask_stack (numpy.ndarray): A 3D NumPy array containing a stack of binary masks.
                                   Each 2D mask represents segmented objects with labeled regions.
                                   Non-zero values in each mask indicate different segments.
        threshold_size (int, optional): The minimum area (in pixels) for a segment to be considered significant
                                        and not removed. Segments with an area less than threshold_size will be
                                        set to 0 (removed). Default value is 1000.

    Returns:
        numpy.ndarray: A modified version of the input mask_stack with small segments removed.

    Note:
        This function modifies the input mask_stack in place. If you want to preserve the original data,
        make a copy of the mask_stack before calling this function.

    Examples:
        # Example usage:
        import numpy as np
        from skimage.measure import regionprops

        # Assuming you have a 3D mask_stack and want to remove segments smaller than 500 pixels.
        modified_mask_stack = remove_small_segments(mask_stack, threshold_size=500)
    """
    # Check the dimensionality of the input mask_stack
    if len(mask_stack.shape) != 3:
        raise ImageDimensionError(expected_dimensionality=3, received_dimensionality=len(mask_stack.shape))

    # Iterate over each frame (2D mask) in the mask_stack
    for n, frame in tqdm(enumerate(mask_stack), desc='Iterating over frames', total=len(mask_stack)):
        # Get coordinates of segments with area less than threshold_size using regionprops
        coords = [props.coords for props in regionprops(frame) if props.area < threshold_size]

        # Iterate over each segment's coordinates and set them to 0 (remove small segments)
        for segment_coords in coords:
            for x, y in segment_coords:
                frame[x, y] = 0

    return mask_stack


def instance_to_semantic(instance_image):
    """
    Quick function to change instance segmentation map to semantic segmentation
    """

    # check dimensionality of image
    if len(instance_image.shape) == 3:

        # create empty list to store semantic frames in
        semantic_stack = list()

        # iterate over each frame
        for frame in tqdm(instance_image, total=len(instance_image), desc='Iterating over frames'):

            # Get unique labels from the instance image
            unique_labels = np.unique(frame)

            # Create a blank semantic segmentation map
            semantic_map = np.zeros_like(frame, dtype=np.uint8)

            # Assign unique labels to the semantic map preserving boundaries
            for sc_label in tqdm(unique_labels[1:], leave=False):

                # get single cell label
                segment = frame == sc_label

                # erode segment so that it doesnt touch neighbours
                eroded_segment = binary_erosion(segment, footprint=np.ones((5, 5)))

                # relabel segment semantically
                semantic_map[eroded_segment] = 1

                # set background to zero
                semantic_map[frame == 0] = 0

                # set dtype
                semantic_map = semantic_map.astype('i2')

            # append results to stack
            semantic_stack.append(semantic_map)

        # convert from list to stack
        semantic_map = np.stack(semantic_stack, axis=0)

    # if it's just a frame then do not iterate over
    elif len(instance_image.shape) == 2:

        # Get unique labels from the instance image
        unique_labels = np.unique(instance_image)

        # Create a blank semantic segmentation map
        semantic_map = np.zeros_like(instance_image, dtype=np.uint8)

        # Assign unique labels to the semantic map preserving boundaries
        for sc_label in tqdm(unique_labels[1:], leave=False):

            # get single cell label
            segment = instance_image == sc_label

            # erode segment so that it doesnt touch neighbours
            eroded_segment = binary_erosion(segment, footprint=np.ones((5, 5)))

            # relabel segment semantically
            semantic_map[eroded_segment] = 1

            # set background to zero
            semantic_map[frame == 0] = 0

            # set dtype
            semantic_map = semantic_map.astype('i2')

    else:
        raise ImageDimensionError(expected_dimensionality="2 or 3", received_dimensionality=len(instance_image.shape))

    return semantic_map


def semantic_to_instance(semantic_image):
    """
    Quick function to change semantic segmentation map to instance segmentation
    """

    # check dimensionality of image
    if len(semantic_image.shape) == 3:

        # create empty list for stack
        instance_stack = list()

        # iterate over frames in stack
        for frame in tqdm(semantic_image, total=len(semantic_image), desc='Iterating over frames'):

            # Get unique labels from the instance image
            instance_image = label(frame)

            # append to stack
            instance_stack.append(instance_image)

        # stack together
        instance_image = np.stack(instance_stack, axis=0)

    # if it's just a frame then do not iterate over
    elif len(semantic_image.shape) == 2:

        # get unique labels from single frame
        instance_image = label(semantic_image)

    else:
        raise ImageDimensionError(expected_dimensionality="2 or 3", received_dimensionality=len(instance_image.shape))

    return instance_image
