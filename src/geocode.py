from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


geolocator = Nominatim(
    user_agent="parking-location-intelligence-map",
    timeout=15
)

rate_limited_geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1,
    max_retries=2,
    error_wait_seconds=2
)


def geocode_address(address: str):
    """
    Converts an address into latitude and longitude using OpenStreetMap Nominatim.
    Returns None if the address cannot be found.
    """

    if not address or not str(address).strip():
        return None

    location = rate_limited_geocode(str(address).strip())

    if location is None:
        return None

    return {
        "lat": location.latitude,
        "lon": location.longitude,
        "display_name": location.address
    }
    