import numpy as np

def plane_correction(height_map):
    """
    Remove tilt/offset by fitting a plane (z = a*x + b*y + c)
    and subtracting it from the height data.

    Args:
        height_map (np.ndarray): 2D height array.

    Returns:
        corrected (np.ndarray): plane-corrected height map
        plane (np.ndarray): fitted plane (same shape)
        coeffs (a, b, c): plane coefficients
    """
    if height_map.ndim != 2:
        raise ValueError("Input must be a 2D array")

    nrows, ncols = height_map.shape
    y, x = np.mgrid[:nrows, :ncols]

    # Flatten for least-squares
    X = np.column_stack((x.ravel(), y.ravel(), np.ones_like(x).ravel()))
    Z = height_map.ravel()

    # Least-squares plane fit
    coeffs, *_ = np.linalg.lstsq(X, Z, rcond=None)
    a, b, c = coeffs

    plane = (a * x + b * y + c)
    corrected = height_map - plane

    return corrected, plane, (a, b, c)