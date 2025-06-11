"""Utility helper functions for Face Invaders."""

def find_overlap_bounds(bounds_1, bounds_2):
    '''
    Return bounds (xmin, xmax, ymin, ymax) of overlapping area between two input bounds.
    Return None if no overlap exists.
    
    Parameters:
    - bounds_1: Tuple of (xmin, xmax, ymin, ymax) for first object
    - bounds_2: Tuple of (xmin, xmax, ymin, ymax) for second object
    
    Returns:
    - Tuple of (xmin, xmax, ymin, ymax) for overlapping region, or None if no overlap
    '''
    # Calculate the overlapping region
    overlap_xmin = max(bounds_1[0], bounds_2[0])
    overlap_xmax = min(bounds_1[1], bounds_2[1])
    overlap_ymin = max(bounds_1[2], bounds_2[2])
    overlap_ymax = min(bounds_1[3], bounds_2[3])

    # Check if there is an actual overlap
    if overlap_xmin < overlap_xmax and overlap_ymin < overlap_ymax:
        return overlap_xmin, overlap_xmax, overlap_ymin, overlap_ymax
    else:
        # No overlap
        return None