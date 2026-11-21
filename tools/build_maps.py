"""Build btg/maps.js: simplified country outlines for each map frame.

Data: Natural Earth 1:50m (public domain). Download the three geojson files
from https://github.com/nvkelso/natural-earth-vector/tree/master/geojson
into a folder and run:  python3 tools/build_maps.py <geojson-folder>
"""
import json, math, sys, os

SRC = sys.argv[1] if len(sys.argv) > 1 else "geo"
OUT = os.path.join(os.path.dirname(__file__), "..", "btg", "maps.js")
W = 640

FRAMES = {
  "france":     {"title": "France", "bbox": [-5.6, 41.2, 10.2, 51.4], "focus": ["FRA"],
                 "cities": [["Paris", 48.857, 2.352], ["Lyon", 45.764, 4.836], ["Bordeaux", 44.838, -0.579],
                            ["Marseille", 43.296, 5.370], ["Strasbourg", 48.573, 7.752], ["Nantes", 47.218, -1.554]],
                 "sea": [["Atlantic", 46.0, -4.2], ["Mediterranean", 42.3, 5.0], ["Channel", 50.2, -2.6]]},
  "italy":      {"title": "Italy", "bbox": [6.2, 36.3, 19.0, 47.3], "focus": ["ITA"],
                 "cities": [["Rome", 41.903, 12.496], ["Milan", 45.464, 9.190], ["Turin", 45.070, 7.687],
                            ["Naples", 40.852, 14.268], ["Florence", 43.769, 11.256], ["Palermo", 38.116, 13.361],
                            ["Venice", 45.440, 12.316]],
                 "sea": [["Tyrrhenian", 40.0, 11.6], ["Adriatic", 43.0, 15.2], ["Ionian", 37.6, 17.6]]},
  "iberia":     {"title": "Spain & Portugal", "bbox": [-11.0, 35.8, 4.6, 44.6], "focus": ["ESP", "PRT"],
                 "cities": [["Madrid", 40.417, -3.704], ["Barcelona", 41.385, 2.173], ["Lisbon", 38.722, -9.139],
                            ["Porto", 41.150, -8.611], ["Seville", 37.389, -5.984], ["Santiago", 42.878, -8.545]],
                 "sea": [["Atlantic", 40.0, -10.2], ["Mediterranean", 38.6, 1.6], ["Bay of Biscay", 44.2, -4.0]]},
  "canarias":   {"title": "Canary Islands", "bbox": [-18.3, 27.5, -13.2, 29.5], "focus": ["ESP"],
                 "cities": [["Santa Cruz", 28.464, -16.251], ["Las Palmas", 28.124, -15.430]],
                 "peaks": [["Teide", 28.272, -16.642]],
                 "sea": [["Atlantic", 29.25, -17.6]]},
  "california": {"title": "California", "bbox": [-124.6, 32.3, -114.0, 42.2], "focus_state": "California",
                 "cities": [["San Francisco", 37.775, -122.419], ["Sacramento", 38.582, -121.494],
                            ["Los Angeles", 34.052, -118.244], ["San Diego", 32.716, -117.161]],
                 "sea": [["Pacific", 35.2, -123.6]]},
}

def load(name):
    with open(os.path.join(SRC, name + ".geojson")) as f:
        return json.load(f)["features"]

def rings(geom):
    if geom["type"] == "Polygon":
        return geom["coordinates"]
    if geom["type"] == "MultiPolygon":
        return [r for p in geom["coordinates"] for r in p]
    return []

def proj(bbox):
    lon0, lat0, lon1, lat1 = bbox
    c = math.cos(math.radians((lat0 + lat1) / 2))
    k = W / ((lon1 - lon0) * c)
    H = (lat1 - lat0) * k
    return (lambda lon, lat: ((lon - lon0) * c * k, (lat1 - lat) * k)), H

def ring_path(ring, P, bbox, pad=1.5):
    lon0, lat0, lon1, lat1 = bbox
    xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
    if max(xs) < lon0 - pad or min(xs) > lon1 + pad or max(ys) < lat0 - pad or min(ys) > lat1 + pad:
        return ""
    pts, last = [], None
    for lon, lat in ring:
        x, y = P(lon, lat)
        if last and abs(x - last[0]) + abs(y - last[1]) < 0.9:
            continue
        pts.append((x, y)); last = (x, y)
    if len(pts) < 3:
        return ""
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"

def geom_path(geom, P, bbox):
    return "".join(ring_path(r, P, bbox) for r in rings(geom))

countries = load("ne_50m_admin_0_countries")
states = load("ne_50m_admin_1_states_provinces")
lakes = load("ne_50m_lakes")

out = {}
for key, fr in FRAMES.items():
    P, H = proj(fr["bbox"])
    focus, other = [], []
    if "focus_state" in fr:
        for f in states:
            pr = f["properties"]
            if pr.get("adm0_a3") != "USA":
                continue
            d = geom_path(f["geometry"], P, fr["bbox"])
            if d:
                (focus if pr.get("name") == fr["focus_state"] else other).append(d)
        for f in countries:
            if f["properties"]["ADM0_A3"] == "MEX":
                d = geom_path(f["geometry"], P, fr["bbox"])
                if d: other.append(d)
    else:
        for f in countries:
            a3 = f["properties"]["ADM0_A3"]
            d = geom_path(f["geometry"], P, fr["bbox"])
            if d:
                (focus if a3 in fr["focus"] else other).append(d)
    lk = [d for d in (geom_path(f["geometry"], P, fr["bbox"]) for f in lakes) if d]
    pt = lambda rows: [[n, *[round(v, 1) for v in P(lon, lat)]] for n, lat, lon in rows]
    out[key] = {"title": fr["title"], "w": W, "h": round(H, 1), "bbox": fr["bbox"],
                "focus": "".join(focus), "other": "".join(other), "lakes": "".join(lk),
                "cities": pt(fr["cities"]), "peaks": pt(fr.get("peaks", [])), "sea": pt(fr["sea"])}

with open(OUT, "w") as f:
    f.write("/* Generated by tools/build_maps.py from Natural Earth 1:50m (public domain). */\n")
    f.write("window.BTG_MAPS=" + json.dumps(out, separators=(",", ":")) + ";\n")
print(OUT, os.path.getsize(OUT), "bytes")
