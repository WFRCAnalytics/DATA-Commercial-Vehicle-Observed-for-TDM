"""Download FHWA's full HPMS extract for Utah (2023) and cache it locally.

Source: https://geo.dot.gov/server/rest/services/Hosted/HPMS_FULL_UT_2023/FeatureServer/0
Statewide, all fields, ~341K road segments (most local roads have no AADT --
only federal-aid roads and sampled local roads carry traffic counts).

Run manually (not part of `quarto render`) whenever the cached copy needs
refreshing:

    python scripts/fetch_hpms_full_ut_2023.py

Writes data/HPMS_FULL_UT_2023.gpkg (~100+ MB -- large; see note in README about
whether to commit this or .gitignore it and re-run the script instead).
"""

import time

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import shape

BASE = "https://geo.dot.gov/server/rest/services/Hosted/HPMS_FULL_UT_2023/FeatureServer/0/query"
PAGE_SIZE = 2000
OUT_GPKG = "data/HPMS_FULL_UT_2023.gpkg"
OUT_LAYER = "HPMS_FULL_UT_2023"


def fetch_all():
    features = []
    offset = 0
    while True:
        params = {
            "where": "1=1",
            "outFields": "*",
            "outSR": 4326,
            "returnGeometry": "true",
            "resultOffset": offset,
            "resultRecordCount": PAGE_SIZE,
            "f": "geojson",
        }
        for attempt in range(3):
            try:
                r = requests.get(BASE, params=params, timeout=120)
                r.raise_for_status()
                gj = r.json()
                break
            except Exception as e:
                print(f"  retry offset={offset} attempt={attempt} err={e}")
                time.sleep(2)
        else:
            raise RuntimeError(f"Failed to fetch page at offset {offset}")

        feats = gj.get("features", [])
        features.extend(feats)
        print(f"  offset={offset} got={len(feats)} total={len(features)}")
        if len(feats) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
        time.sleep(0.1)
    return features


def main():
    print("Downloading full HPMS_FULL_UT_2023 layer (statewide, all fields)...")
    features = fetch_all()
    print(f"Total features fetched: {len(features)}")

    rows = [f["properties"] for f in features]
    geoms = [shape(f["geometry"]) if f.get("geometry") else None for f in features]

    gdf = gpd.GeoDataFrame(pd.DataFrame(rows), geometry=geoms, crs="EPSG:4326")

    print(f"Writing {len(gdf)} rows to {OUT_GPKG} ...")
    gdf.to_file(OUT_GPKG, driver="GPKG", layer=OUT_LAYER)
    print("Done.")


if __name__ == "__main__":
    main()
