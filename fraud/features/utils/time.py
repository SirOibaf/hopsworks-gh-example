def time_delta(datetime_value, shift):
    """Compute time difference between each consecutive transaction."""

    time_shifted = datetime_value.shift(shift)
    return time_shifted
