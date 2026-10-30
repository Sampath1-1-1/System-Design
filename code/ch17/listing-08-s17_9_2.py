# Extracted from manuscript/book1-traditional/17-data-structures-for-scale.md §17.9.2 (listing 8). Edit the manuscript, not this file.
import math
import random
from collections import defaultdict

BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"          # no a, i, l, o

def encode(lat: float, lon: float, length: int) -> str:
    """Interleave longitude and latitude bisection bits (longitude first), 5 bits per character."""
    lat_rng, lon_rng = [-90.0, 90.0], [-180.0, 180.0]
    out, bits, bit_count, even = [], 0, 0, True
    while len(out) < length:
        rng, val = (lon_rng, lon) if even else (lat_rng, lat)
        mid = (rng[0] + rng[1]) / 2
        if val >= mid:
            bits, rng[0] = (bits << 1) | 1, mid
        else:
            bits, rng[1] = bits << 1, mid
        even, bit_count = not even, bit_count + 1
        if bit_count == 5:
            out.append(BASE32[bits])
            bits, bit_count = 0, 0
    return "".join(out)

def decode_box(gh: str):
    """Return (lat_min, lat_max, lon_min, lon_max) of a geohash cell."""
    lat_rng, lon_rng, even = [-90.0, 90.0], [-180.0, 180.0], True
    for ch in gh:
        v = BASE32.index(ch)
        for shift in range(4, -1, -1):
            rng = lon_rng if even else lat_rng
            mid = (rng[0] + rng[1]) / 2
            if (v >> shift) & 1:
                rng[0] = mid
            else:
                rng[1] = mid
            even = not even
    return lat_rng[0], lat_rng[1], lon_rng[0], lon_rng[1]

def neighbors(gh: str):
    """The 8 surrounding cells (center-offset method; ignores the poles and the antimeridian)."""
    la0, la1, lo0, lo1 = decode_box(gh)
    dlat, dlon = la1 - la0, lo1 - lo0
    clat, clon = (la0 + la1) / 2, (lo0 + lo1) / 2
    return [encode(clat + i * dlat, clon + j * dlon, len(gh))
            for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]

def covering(lat: float, lon: float, radius_km: float, length: int):
    """All cells of this length that intersect the circle's bounding box (exact recall)."""
    la0, la1, lo0, lo1 = decode_box(encode(lat, lon, length))
    dlat, dlon = la1 - la0, lo1 - lo0
    ri = math.ceil(radius_km / (dlat * 111.0))             # rows needed above and below
    rj = math.ceil(radius_km / (dlon * 111.0 * math.cos(math.radians(lat))))
    clat, clon = (la0 + la1) / 2, (lo0 + lo1) / 2
    return [encode(clat + i * dlat, clon + j * dlon, length)
            for i in range(-ri, ri + 1) for j in range(-rj, rj + 1)]

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

print("encode(57.64911, 10.40744, 11) =", encode(57.64911, 10.40744, 11))   # reference: u4pruydqqvj

print(f"{'len':>3} {'bits':>4} {'cell width (equator)':>21} {'cell height':>12}")
for length in range(1, 11):
    lon_bits = math.ceil(5 * length / 2)
    lat_bits = 5 * length // 2
    w_km = 360 / 2 ** lon_bits * 111.32
    h_km = 180 / 2 ** lat_bits * 110.57
    fmt = lambda km: f"{km:,.1f} km" if km >= 1 else f"{km * 1000:,.2f} m"
    print(f"{length:3d} {5 * length:4d} {fmt(w_km):>21} {fmt(h_km):>12}")

# Proximity search: 200,000 drivers around San Francisco; find those within 1 km of a rider
rng = random.Random(3)
drivers = [(37.70 + rng.random() * 0.12, -122.52 + rng.random() * 0.14) for _ in range(200_000)]
rider = (37.7749, -122.4194)
truth = {i for i, d in enumerate(drivers) if haversine_km(*rider, *d) <= 1.0}
for P, method in ((6, "3x3"), (5, "3x3"), (6, "cover")):
    index = defaultdict(list)                        # geohash -> driver ids (in production: a sorted key range)
    for i, (lat, lon) in enumerate(drivers):
        index[encode(lat, lon, P)].append(i)
    cell = encode(*rider, P)
    cells = [cell] + neighbors(cell) if method == "3x3" else covering(*rider, 1.0, P)
    candidates = [i for c in cells for i in index[c]]
    hits = {i for i in candidates if haversine_km(*rider, *drivers[i]) <= 1.0}
    la0, la1, lo0, lo1 = decode_box(cell)
    print(f"P={P} {method:5s} cell {cell}: {haversine_km(la0, lo0, la0, lo1) * 1000:,.0f} m x "
          f"{haversine_km(la0, lo0, la1, lo0) * 1000:,.0f} m; {len(cells)} cells -> "
          f"{len(candidates):,} candidates, {len(hits):,} within 1 km, "
          f"recall {len(hits) / len(truth):.3f} (brute force finds {len(truth):,})")
