"""Summarize FHWA HPMS (2023) truck VMT by super-district (county) and facility type.

Reads:
  data/HPMS_FULL_UT_2023.gpkg        -- full statewide HPMS extract (see
                                         scripts/fetch_hpms_full_ut_2023.py)
  data/WFv1000_TAZ__DSUP.geojson     -- model super-districts (whole counties,
                                         or the model-area slice of a county)

For each HPMS segment with a reported AADT, computes daily VMT:
  Total VMT  = aadt * segment length (miles)
  Medium VMT = aadt_single_unit * segment length
  Heavy VMT  = aadt_combination * segment length

Segments are assigned to a super-district by their centroid (point-in-polygon),
and to a facility type by rolling HPMS's F_SYSTEM code into the same six
categories used in cv-observed-for-tdm.qmd.

Run manually:
    python scripts/build_hpms_vmt_by_county_facility.py

Writes data_processed/HPMS_2023_VMT_by_SuperDistrict_FunctionalClass.csv
"""

import geopandas as gpd
import pandas as pd
import pyogrio

CRS_UTM = 26912  # NAD83 / UTM zone 12N -- matches cv-observed-for-tdm.qmd

HPMS_GPKG = "data/HPMS_FULL_UT_2023.gpkg"
DSUP_GEOJSON = "data/WFv1000_TAZ__DSUP.geojson"
OUT_CSV = "data_processed/HPMS_2023_VMT_by_SuperDistrict_FunctionalClass.csv"

FSYS_LABELS = {
    1: "Freeway",
    2: "Expressway",
    3: "Principal Arterial",
    4: "Minor Arterial",
    5: "Collector",
    6: "Collector",
    7: "Local",
}
FT_ORDER = ["Freeway", "Expressway", "Principal Arterial", "Minor Arterial", "Collector", "Local"]


def main():
    dsup_wgs84 = gpd.read_file(DSUP_GEOJSON)
    dsup = dsup_wgs84.to_crs(CRS_UTM)
    minx, miny, maxx, maxy = dsup_wgs84.total_bounds

    # pyogrio reads only the needed columns + a bbox-filtered row set directly
    # from the GeoPackage's spatial index -- geopandas.read_file (fiona engine)
    # is far slower against a 340K-row / ~90-column file like this one.
    seg = pyogrio.read_dataframe(
        HPMS_GPKG,
        columns=["f_system", "aadt", "aadt_single_unit", "aadt_combination", "beginpoint", "endpoint"],
        bbox=(minx, miny, maxx, maxy),
    )
    seg = seg[seg["aadt"].notna()].to_crs(CRS_UTM)
    print(f"DSUP super-districts: {len(dsup)}; HPMS segments in bbox with AADT: {len(seg)}")

    seg["length_mi"] = seg["endpoint"] - seg["beginpoint"]
    seg = seg[seg["length_mi"] > 0].copy()

    seg["Total"] = seg["aadt"] * seg["length_mi"]
    seg["MD"] = seg["aadt_single_unit"].fillna(0) * seg["length_mi"]
    seg["HV"] = seg["aadt_combination"].fillna(0) * seg["length_mi"]
    seg["Functional Class"] = seg["f_system"].map(FSYS_LABELS)

    seg_pts = seg.copy()
    seg_pts["geometry"] = seg_pts.geometry.centroid

    joined = gpd.sjoin(seg_pts, dsup[["DSUP_NAME", "geometry"]], how="inner", predicate="within")
    print(f"Matched {len(joined)} of {len(seg)} segments to a super-district")

    summary = joined.groupby(["DSUP_NAME", "Functional Class"])[["Total", "MD", "HV"]].sum().reset_index()

    district_totals = summary.groupby("DSUP_NAME")[["Total", "MD", "HV"]].sum().reset_index()
    district_totals["Functional Class"] = "All Classes"
    summary = pd.concat([summary, district_totals], ignore_index=True)

    summary["Functional Class"] = pd.Categorical(
        summary["Functional Class"], categories=FT_ORDER + ["All Classes"], ordered=True
    )
    summary = summary.sort_values(["DSUP_NAME", "Functional Class"]).reset_index(drop=True)

    summary.to_csv(OUT_CSV, index=False)
    print(f"Saved to {OUT_CSV}")
    print(summary.round(0).to_string(index=False))


if __name__ == "__main__":
    main()
