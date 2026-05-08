"""Location string normalization and matching utilities."""


def normalize_location(location: str) -> str:
    if not location:
        return ""
    return location.lower().strip()


def locations_match(loc1: str, loc2: str) -> bool:
    """Loose match: same city/state/region by substring or comma-split parts."""
    if not loc1 or not loc2:
        return False
    n1, n2 = normalize_location(loc1), normalize_location(loc2)
    if not n1 or not n2:
        return False
    if n1 == n2 or n1 in n2 or n2 in n1:
        return True
    parts1 = [p.strip() for p in n1.split(",")]
    parts2 = [p.strip() for p in n2.split(",")]
    return any(
        p1 and p2 and (p1 == p2 or p1 in p2 or p2 in p1)
        for p1 in parts1 for p2 in parts2
    )
