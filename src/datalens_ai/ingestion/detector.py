from __future__ import annotations

import re

import pandas as pd

# Patterns for semantic type detection
_PATTERNS = {
    "email": re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$"),
    "url": re.compile(r"^https?://\S+$"),
    "phone": re.compile(r"^[\+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]{7,15}$"),
    "zipcode": re.compile(r"^\d{5}(-\d{4})?$"),
    "ip_address": re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"),
}

_CURRENCY_PATTERN = re.compile(
    r"^[$\u20ac\u00a3\u00a5\u20b9]\s?[\d,]+\.?\d*$|^[\d,]+\.?\d*\s?[$\u20ac\u00a3\u00a5\u20b9]$"
)
_PERCENTAGE_PATTERN = re.compile(r"^-?[\d.]+\s?%$")

# Country names (subset for detection)
_COUNTRY_NAMES = {
    "united states", "china", "india", "japan", "germany", "united kingdom",
    "france", "brazil", "italy", "canada", "australia", "spain", "mexico",
    "indonesia", "netherlands", "turkey", "switzerland", "argentina",
    "sweden", "poland", "belgium", "norway", "austria", "ireland",
    "usa", "uk", "us",
}


def detect_semantic_type(series: pd.Series, column_name: str) -> str | None:
    """Detect semantic type from column values and name.

    Returns a short label such as ``"email"``, ``"currency"``, ``"country"``,
    etc., or ``None`` when no semantic type can be inferred.
    """
    name_lower = column_name.lower().strip()

    # Name-based heuristics (fast)
    if any(x in name_lower for x in ("_id", "id_", "uuid")):
        if name_lower.endswith("_id") or name_lower.startswith("id"):
            return "id"
    if any(x in name_lower for x in ("email", "e_mail")):
        return "email"
    if any(x in name_lower for x in ("url", "link", "website", "href")):
        return "url"
    if any(x in name_lower for x in ("phone", "tel", "mobile", "cell")):
        return "phone"
    if any(x in name_lower for x in ("country", "nation")):
        return "country"
    if any(x in name_lower for x in ("city", "town")):
        return "city"
    if any(x in name_lower for x in ("state", "province", "region")):
        return "state"
    if any(x in name_lower for x in ("zip", "postal")):
        return "zipcode"
    if any(x in name_lower for x in ("lat", "latitude")):
        return "latitude"
    if any(x in name_lower for x in ("lon", "lng", "longitude")):
        return "longitude"
    if any(
        x in name_lower
        for x in ("price", "cost", "revenue", "amount", "salary", "income", "fee")
    ):
        return "currency"
    if any(x in name_lower for x in ("pct", "percent", "rate", "ratio")):
        return "percentage"
    if any(
        x in name_lower for x in ("name", "first_name", "last_name", "full_name")
    ):
        return "name"
    if any(
        x in name_lower for x in ("date", "time", "timestamp", "created", "updated")
    ):
        return "date"

    # Value-based detection (sample 20 non-null values)
    sample = series.dropna().astype(str).head(20)
    if len(sample) == 0:
        return None

    # Check regex patterns
    for sem_type, pattern in _PATTERNS.items():
        matches = sum(1 for v in sample if pattern.match(v.strip()))
        if matches / len(sample) > 0.7:
            return sem_type

    # Check currency
    currency_matches = sum(1 for v in sample if _CURRENCY_PATTERN.match(v.strip()))
    if currency_matches / len(sample) > 0.7:
        return "currency"

    # Check percentage
    pct_matches = sum(1 for v in sample if _PERCENTAGE_PATTERN.match(v.strip()))
    if pct_matches / len(sample) > 0.7:
        return "percentage"

    # Check country names
    lower_vals = set(v.lower().strip() for v in sample)
    if len(lower_vals & _COUNTRY_NAMES) / max(len(lower_vals), 1) > 0.3:
        return "country"

    return None
