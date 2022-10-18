import numpy as np


def haversine(long, lat, shift):
    """Compute Haversine distance between each consecutive coordinate in (long, lat)."""

    long_shifted = long.shift(shift)
    lat_shifted = lat.shift(shift)
    long_diff = long_shifted - long
    lat_diff = lat_shifted - lat

    a = np.sin(lat_diff / 2.0) ** 2
    b = np.cos(lat) * np.cos(lat_shifted) * np.sin(long_diff / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a + b))

    return c
