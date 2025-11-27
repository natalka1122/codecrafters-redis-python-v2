import math
from app.const import EARTH_RADIUS_IN_METERS
D_R = math.pi / 180.0


def deg_rad(ang: float) -> float:
    return ang * D_R


def geohashGetLatDistance(lat1d: float, lat2d: float) -> float:
    return EARTH_RADIUS_IN_METERS * abs(deg_rad(lat2d) - deg_rad(lat1d))


# Calculate distance using haversine great circle distance formula
def geohashGetDistance(  # noqa: WPS210
    lon1d: float, lat1d: float, lon2d: float, lat2d: float
) -> float:
    lon1r = deg_rad(lon1d)
    lon2r = deg_rad(lon2d)
    v = math.sin((lon2r - lon1r) / 2)
    # if v == 0 we can avoid doing expensive math when lons are practically the same
    if v == 0:
        return geohashGetLatDistance(lat1d, lat2d)
    lat1r = deg_rad(lat1d)
    lat2r = deg_rad(lat2d)
    u = math.sin((lat2r - lat1r) / 2)
    a = u * u + math.cos(lat1r) * math.cos(lat2r) * v * v  # noqa: WPS221
    return 2.0 * EARTH_RADIUS_IN_METERS * math.asin(math.sqrt(a))
