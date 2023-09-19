def int_or_none(x: str):
    """Convert a string to int. If false, return None."""
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def float_or_none(x: str):
    """Convert a string to float. If false, return None."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
