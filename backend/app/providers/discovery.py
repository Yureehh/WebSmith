from dataclasses import dataclass
from math import cos, radians
from re import escape

import httpx

from app.core.config import settings


@dataclass
class DiscoveredBusiness:
    name: str
    normalized_name: str
    formatted_address: str | None
    lat: float | None
    lng: float | None
    website_url: str | None = None
    phone: str | None = None
    email: str | None = None
    osm_id: str | None = None
    primary_category: str | None = None
    categories: list[str] | None = None
    discovery_source: str = "osm"
    web_source_document: dict | None = None


@dataclass
class DiscoveryResult:
    center: tuple[float, float]
    businesses: list[DiscoveredBusiness]
    coverage: list[dict]
    provider_errors: list[dict]
    total_seen_count: int
    excluded_count: int


ITALIAN_FALLBACK_COORDS = {
    "milano": (45.4642, 9.19),
    "milan": (45.4642, 9.19),
    "roma": (41.9028, 12.4964),
    "rome": (41.9028, 12.4964),
    "torino": (45.0703, 7.6869),
    "napoli": (40.8518, 14.2681),
    "bologna": (44.4949, 11.3426),
    "firenze": (43.7696, 11.2558),
    "forli": (44.2227, 12.0407),
    "forlì": (44.2227, 12.0407),
    "via delle torri": (44.2222, 12.0414),
}

SEARCH_KEYS = [
    "shop",
    "amenity",
    "tourism",
    "office",
    "craft",
    "leisure",
    "healthcare",
    "social_facility",
]
CATEGORY_ALIASES = {
    "bar": {"amenity": ["bar", "cafe", "pub"]},
    "cafe": {"amenity": ["cafe", "bar"]},
    "caffè": {"amenity": ["cafe", "bar"]},
    "ristorante": {"amenity": ["restaurant", "fast_food"]},
    "restaurant": {"amenity": ["restaurant", "fast_food"]},
    "dentist": {"amenity": ["dentist"], "healthcare": ["dentist"]},
    "dentista": {"amenity": ["dentist"], "healthcare": ["dentist"]},
    "hotel": {"tourism": ["hotel", "guest_house", "bed_and_breakfast"]},
    "b&b": {"tourism": ["guest_house", "bed_and_breakfast", "hotel"]},
    "bakery": {"shop": ["bakery", "pastry"]},
    "panificio": {"shop": ["bakery", "pastry"]},
    "palestra": {"leisure": ["fitness_centre"], "shop": ["sports"]},
    "gym": {"leisure": ["fitness_centre"], "shop": ["sports"]},
    "parrucchiere": {"shop": ["hairdresser", "beauty"]},
    "hairdresser": {"shop": ["hairdresser", "beauty"]},
    "meccanico": {"shop": ["car_repair"], "craft": ["mechanic"]},
    "mechanic": {"shop": ["car_repair"], "craft": ["mechanic"]},
    "fuel": {"amenity": ["fuel", "charging_station"]},
    "gas station": {"amenity": ["fuel", "charging_station"]},
    "benzinaio": {"amenity": ["fuel", "charging_station"]},
    "pharmacy": {"amenity": ["pharmacy"], "healthcare": ["pharmacy"]},
    "farmacia": {"amenity": ["pharmacy"], "healthcare": ["pharmacy"]},
    "post office": {"amenity": ["post_office"]},
    "posta": {"amenity": ["post_office"]},
    "poste": {"amenity": ["post_office"]},
    "poste italiane": {"amenity": ["post_office"]},
    "beauty": {"shop": ["beauty", "cosmetics"]},
    "estate agent": {"office": ["estate_agent"]},
    "real estate": {"office": ["estate_agent"]},
    "lawyer": {"office": ["lawyer"]},
    "architect": {"office": ["architect"]},
    "associazione": {"office": ["association", "ngo"], "amenity": ["community_centre"]},
    "association": {"office": ["association", "ngo"], "amenity": ["community_centre"]},
    "charity": {"shop": ["charity"], "office": ["association", "ngo"]},
    "cooperativa": {
        "office": ["association", "ngo"],
        "amenity": ["social_facility", "community_centre"],
    },
    "cooperative": {
        "office": ["association", "ngo"],
        "amenity": ["social_facility", "community_centre"],
    },
    "impresa sociale": {
        "office": ["association", "ngo"],
        "amenity": ["social_facility", "community_centre"],
    },
    "nonprofit": {"office": ["association", "ngo"], "amenity": ["community_centre"]},
    "servizi disabilità": {"amenity": ["social_facility"], "social_facility": ["day_care"]},
    "social enterprise": {
        "office": ["association", "ngo"],
        "amenity": ["social_facility", "community_centre"],
    },
    "optician": {"shop": ["optician"]},
    "clothes": {"shop": ["clothes"]},
    "supermarket": {"shop": ["supermarket", "convenience"]},
    "bank": {"amenity": ["bank", "atm"]},
    "atm": {"amenity": ["atm"]},
    "church": {"amenity": ["place_of_worship"], "building": ["church"]},
    "place of worship": {"amenity": ["place_of_worship"]},
    "religious": {"amenity": ["place_of_worship"]},
    "police": {"amenity": ["police"]},
    "carabinieri": {"amenity": ["police"]},
    "public safety": {"amenity": ["police", "fire_station"]},
    "courthouse": {"amenity": ["courthouse"]},
    "government": {"office": ["government"], "amenity": ["townhall"]},
    "townhall": {"amenity": ["townhall"]},
    "public office": {"office": ["government"], "amenity": ["townhall"]},
    "legal": {"office": ["lawyer"]},
    "law office": {"office": ["lawyer"]},
    "school": {"amenity": ["school", "university", "college"]},
    "university": {"amenity": ["university", "college"]},
    "hospital": {"amenity": ["hospital"], "healthcare": ["hospital"]},
    "emergency": {"amenity": ["hospital", "fire_station"], "healthcare": ["hospital"]},
}

DEFAULT_EXCLUDED_CATEGORIES = [
    "fuel",
    "bank",
    "atm",
    "church",
    "place of worship",
    "religious",
    "police",
    "carabinieri",
    "public safety",
    "courthouse",
    "government",
    "townhall",
    "public office",
    "post office",
    "poste",
    "pharmacy",
    "farmacia",
    "supermarket",
    "convenience",
    "school",
    "university",
    "hospital",
    "emergency",
]


def normalize_name(name: str) -> str:
    return " ".join(name.lower().strip().split())


def format_address(tags: dict) -> str | None:
    if tags.get("addr:full"):
        return tags["addr:full"]
    parts = [
        " ".join(
            value for value in [tags.get("addr:street"), tags.get("addr:housenumber")] if value
        ),
        tags.get("addr:postcode"),
        tags.get("addr:city"),
    ]
    address = ", ".join(part for part in parts if part)
    return address or None


def category_query_lines(
    key: str, values: list[str], radius_m: int, lat: float, lng: float
) -> list[str]:
    value_regex = "|".join(escape(value) for value in values)
    return [
        f'node["name"]["{key}"~"^({value_regex})$"](around:{radius_m},{lat},{lng});',
        f'way["name"]["{key}"~"^({value_regex})$"](around:{radius_m},{lat},{lng});',
    ]


def alias_values(term: str) -> set[str]:
    normalized = normalize_name(term)
    aliases = CATEGORY_ALIASES.get(normalized)
    if not aliases:
        return {normalized}
    values = {normalized}
    for alias_group in aliases.values():
        values.update(normalize_name(value) for value in alias_group)
    return values


def category_matches(categories: list[str] | None, filters: set[str]) -> bool:
    normalized_categories = {normalize_name(category) for category in categories or []}
    return bool(normalized_categories & filters)


def business_matches_activity_filters(
    business: DiscoveredBusiness, categories: list[str], excluded_categories: list[str]
) -> bool:
    category_values = [
        *(business.categories or []),
        business.primary_category or "",
    ]
    normalized_categories = {normalize_name(category) for category in category_values if category}
    normalized_name = normalize_name(business.name)
    include_filters = set().union(*(alias_values(term) for term in categories if term.strip()))
    exclude_filters = set().union(
        *(alias_values(term) for term in excluded_categories if term.strip())
    )

    normalized_blob = " ".join([normalized_name, *normalized_categories]).replace("_", " ")
    if exclude_filters and (
        normalized_categories & exclude_filters
        or any(filter_term.replace("_", " ") in normalized_blob for filter_term in exclude_filters)
    ):
        return False
    if not include_filters:
        return True
    return bool(normalized_categories & include_filters) or any(
        filter_term in normalized_name for filter_term in include_filters
    )


def generic_query_lines(radius_m: int, lat: float, lng: float) -> list[str]:
    lines = []
    for key in SEARCH_KEYS:
        lines.append(f'node["name"]["{key}"](around:{radius_m},{lat},{lng});')
        lines.append(f'way["name"]["{key}"](around:{radius_m},{lat},{lng});')
    return lines


def build_overpass_query(
    center: tuple[float, float], radius_m: int, max_results: int, query_terms: list[str]
) -> str:
    lines = []
    for raw_term in query_terms:
        term = normalize_name(raw_term)
        aliases = CATEGORY_ALIASES.get(term)
        if aliases:
            for key, values in aliases.items():
                lines.extend(category_query_lines(key, values, radius_m, center[0], center[1]))
    if not lines:
        lines = generic_query_lines(radius_m, center[0], center[1])
    body = "\n      ".join(lines)
    return f"""
    [out:json][timeout:18];
    (
      {body}
    );
    out center {max_results};
    """


def build_search_tiles(center: tuple[float, float], radius_km: float, depth: str) -> list[dict]:
    radius = max(radius_km, 0.1)
    if depth == "fast" or radius <= 1:
        return [
            {
                "id": "center",
                "label": "Center",
                "lat": center[0],
                "lng": center[1],
                "radius_km": radius,
                "status": "pending",
                "result_count": 0,
                "error": None,
            }
        ]

    grid = [(-0.55, -0.55), (-0.55, 0.55), (0.55, -0.55), (0.55, 0.55)]
    if depth == "deep":
        grid = [
            (-0.66, -0.66),
            (-0.66, 0),
            (-0.66, 0.66),
            (0, -0.66),
            (0, 0),
            (0, 0.66),
            (0.66, -0.66),
            (0.66, 0),
            (0.66, 0.66),
        ]
    lng_scale = max(cos(radians(center[0])), 0.2)
    tile_radius = radius * (0.62 if depth == "deep" else 0.74)
    tiles = []
    for index, (lat_offset, lng_offset) in enumerate(grid, start=1):
        tiles.append(
            {
                "id": f"tile-{index}",
                "label": f"Tile {index}",
                "lat": center[0] + (lat_offset * radius / 111),
                "lng": center[1] + (lng_offset * radius / (111 * lng_scale)),
                "radius_km": tile_radius,
                "status": "pending",
                "result_count": 0,
                "error": None,
            }
        )
    return tiles


async def geocode_location(location_query: str) -> tuple[float, float]:
    key = normalize_name(location_query).split(",")[0]
    if key in ITALIAN_FALLBACK_COORDS:
        return ITALIAN_FALLBACK_COORDS[key]

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(
                f"{settings.nominatim_url}/search",
                params={"q": f"{location_query}, Italy", "format": "json", "limit": 1},
                headers={"User-Agent": "WebSmith/0.1 local app"},
            )
            response.raise_for_status()
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return ITALIAN_FALLBACK_COORDS["milano"]


async def discover_osm(
    location_query: str,
    radius_km: float,
    max_results: int,
    categories: list[str],
    excluded_categories: list[str],
    keywords: str | None,
    name_query: str | None = None,
    search_depth: str = "balanced",
) -> DiscoveryResult:
    center = await geocode_location(location_query)
    query_terms = categories or ([keywords] if keywords else [])
    display_term = ", ".join(query_terms) if query_terms else "business"
    tiles = build_search_tiles(center, radius_km, search_depth)
    businesses: list[DiscoveredBusiness] = []
    provider_errors: list[dict] = []
    total_seen_count = 0
    excluded_count = 0

    async with httpx.AsyncClient(timeout=18) as client:
        for tile in tiles:
            remaining_provider_budget = max_results - total_seen_count
            if remaining_provider_budget <= 0:
                break
            search_radius_m = max(int(tile["radius_km"] * 1000), 100)
            per_tile_limit = min(remaining_provider_budget, 200)
            overpass_query = build_overpass_query(
                (tile["lat"], tile["lng"]),
                search_radius_m,
                per_tile_limit,
                query_terms,
            )
            try:
                response = await client.post(
                    settings.overpass_url,
                    data={"data": overpass_query},
                    headers={"User-Agent": "WebSmith/0.1 local app (private local lead discovery)"},
                )
                response.raise_for_status()
                elements = response.json().get("elements", [])[:per_tile_limit]
                tile["status"] = "success" if elements else "empty"
            except Exception as exc:
                elements = []
                tile["status"] = "error"
                tile["error"] = str(exc)
                provider_errors.append(
                    {"tile": tile["id"], "provider": "osm_overpass", "error": str(exc)}
                )

            raw_tile_businesses = []
            for element in elements:
                tags = element.get("tags", {})
                name = tags.get("name")
                if not name:
                    continue
                lat = element.get("lat") or element.get("center", {}).get("lat")
                lng = element.get("lon") or element.get("center", {}).get("lon")
                raw_tile_businesses.append(
                    DiscoveredBusiness(
                        name=name,
                        normalized_name=normalize_name(name),
                        formatted_address=format_address(tags),
                        lat=lat,
                        lng=lng,
                        website_url=tags.get("website") or tags.get("contact:website"),
                        phone=tags.get("phone") or tags.get("contact:phone"),
                        osm_id=str(element.get("id")),
                        primary_category=(
                            tags.get("shop")
                            or tags.get("amenity")
                            or tags.get("tourism")
                            or tags.get("office")
                            or tags.get("craft")
                            or tags.get("leisure")
                            or tags.get("healthcare")
                            or tags.get("social_facility")
                            or display_term
                        ),
                        categories=[
                            value
                            for value in [
                                tags.get("shop"),
                                tags.get("amenity"),
                                tags.get("tourism"),
                                tags.get("office"),
                                tags.get("craft"),
                                tags.get("leisure"),
                                tags.get("healthcare"),
                                tags.get("social_facility"),
                            ]
                            if value
                        ],
                    )
                )
            total_seen_count += len(raw_tile_businesses)
            filtered_tile_businesses = [
                business
                for business in raw_tile_businesses
                if business_matches_activity_filters(business, categories, excluded_categories)
                and (not name_query or normalize_name(name_query) in normalize_name(business.name))
            ]
            excluded_count += len(raw_tile_businesses) - len(filtered_tile_businesses)
            tile["result_count"] = len(filtered_tile_businesses)
            businesses.extend(filtered_tile_businesses)

    deduped: list[DiscoveredBusiness] = []
    seen_keys: set[tuple[str, str]] = set()
    for business in businesses:
        key = (
            business.osm_id or business.website_url or business.normalized_name,
            business.formatted_address or "",
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(business)

    return DiscoveryResult(
        center=center,
        businesses=deduped,
        coverage=tiles,
        provider_errors=provider_errors,
        total_seen_count=total_seen_count,
        excluded_count=excluded_count,
    )
