import math
import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"

MILES_TO_METERS = 1609.344
SEARCH_RADIUS_MILES = 5
SEARCH_RADIUS_METERS = int(SEARCH_RADIUS_MILES * MILES_TO_METERS)

RADII_MILES = [1, 3, 5]

CATEGORIES = [
    "nearby_parking_lots",
    "businesses",
    "tourist_attractions",
    "restaurants",
    "venues",
]


def haversine_miles(lat1, lon1, lat2, lon2):
    """
    Distance between two lat/lon points in miles.
    """

    radius_earth_miles = 3958.8

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.asin(math.sqrt(a))

    return radius_earth_miles * c


def build_overpass_query(lat, lon):
    """
    Searches OpenStreetMap around a point for:
    - parking lots
    - businesses
    - tourist attractions
    - restaurants
    - venues
    """

    return f"""
    [out:json][timeout:90];
    (
      nwr["amenity"="parking"](around:{SEARCH_RADIUS_METERS},{lat},{lon});

      nwr["shop"](around:{SEARCH_RADIUS_METERS},{lat},{lon});
      nwr["office"](around:{SEARCH_RADIUS_METERS},{lat},{lon});

      nwr["tourism"~"attraction|museum|hotel|theme_park|zoo|gallery|aquarium|viewpoint"](around:{SEARCH_RADIUS_METERS},{lat},{lon});

      nwr["amenity"~"restaurant|cafe|bar|pub|fast_food|food_court"](around:{SEARCH_RADIUS_METERS},{lat},{lon});

      nwr["amenity"~"theatre|cinema|nightclub|events_venue|arts_centre|conference_centre"](around:{SEARCH_RADIUS_METERS},{lat},{lon});
      nwr["leisure"~"stadium|sports_centre|amusement_arcade|fitness_centre"](around:{SEARCH_RADIUS_METERS},{lat},{lon});
    );
    out center tags;
    """


def get_element_coordinates(element):
    """
    OSM nodes have lat/lon directly.
    OSM ways/relations usually have a center object.
    """

    if "lat" in element and "lon" in element:
        return element["lat"], element["lon"]

    if "center" in element:
        center = element["center"]
        return center.get("lat"), center.get("lon")

    return None, None


def classify_osm_tags(tags):
    """
    One OSM object can count in more than one category.
    Example: a museum can be both a tourist attraction and a venue.
    """

    categories = []

    amenity = tags.get("amenity")
    tourism = tags.get("tourism")
    leisure = tags.get("leisure")

    if amenity == "parking":
        categories.append("nearby_parking_lots")

    if "shop" in tags or "office" in tags:
        categories.append("businesses")

    if tourism in {
        "attraction",
        "museum",
        "hotel",
        "theme_park",
        "zoo",
        "gallery",
        "aquarium",
        "viewpoint",
    }:
        categories.append("tourist_attractions")

    if amenity in {
        "restaurant",
        "cafe",
        "bar",
        "pub",
        "fast_food",
        "food_court",
    }:
        categories.append("restaurants")

    if amenity in {
        "theatre",
        "cinema",
        "nightclub",
        "events_venue",
        "arts_centre",
        "conference_centre",
    } or leisure in {
        "stadium",
        "sports_centre",
        "amusement_arcade",
        "fitness_centre",
    }:
        categories.append("venues")

    return categories


def empty_counts():
    counts = {}

    for category in CATEGORIES:
        for radius in RADII_MILES:
            counts[f"{category}_{radius}mi"] = 0

    return counts


def get_nearby_counts(lat, lon):
    """
    Returns count columns like:
    nearby_parking_lots_1mi
    restaurants_3mi
    venues_5mi
    """

    query = build_overpass_query(lat, lon)

    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        timeout=120
    )

    response.raise_for_status()

    data = response.json()
    elements = data.get("elements", [])

    counts = empty_counts()

    seen_by_category = {
        category: set()
        for category in CATEGORIES
    }

    for element in elements:
        element_lat, element_lon = get_element_coordinates(element)

        if element_lat is None or element_lon is None:
            continue

        tags = element.get("tags", {})
        categories = classify_osm_tags(tags)

        if not categories:
            continue

        distance = haversine_miles(lat, lon, element_lat, element_lon)

        element_key = (
            element.get("type"),
            element.get("id")
        )

        for category in categories:
            # Avoid counting the current parking lot as its own nearby competitor
            if category == "nearby_parking_lots" and distance < 0.05:
                continue

            if element_key in seen_by_category[category]:
                continue

            seen_by_category[category].add(element_key)

            for radius in RADII_MILES:
                if distance <= radius:
                    counts[f"{category}_{radius}mi"] += 1

    return counts

    