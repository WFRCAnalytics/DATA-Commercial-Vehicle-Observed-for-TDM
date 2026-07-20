# DATA-Commercial-Vehicle-Observed-for-TDM

Standalone copy of the WFRC/MAG travel model's truck validation page (originally
`v10x/v1000/validation/qmd-C48/4t-truckvalidation.qmd` in the WF-TDM-Documentation repo),
pulled out with all of its data dependencies so it can be dropped into its own repo and
rendered independently.

It compares Medium (single-unit, "MD") and Heavy (combination-unit, "HV") truck shares
and VMT by facility type across three sources (UDOT CCS counts, HPMS, and the model), and
includes a "Proposed Changes to Truck Classification" section that recomputes those splits
against newer UDOT vehicle-length-class data — the basis for MD/HV adjustment factors by
facility type.

Model run bundled here: **C48** (see `data/Summary_SEGID.csv`, copied from
`_large_files/v1000/v1000-C48/4-assignhwy/Summary_SEGID.csv` in the source repo). To
validate a different run, replace that file with another run's `Summary_SEGID.csv`
(needs at minimum the columns `SEGID, FTCLASS, DISTANCE, DY_Vol_PC, DY_Vol_LT, DY_Vol_MD,
DY_Vol_HV`).

## Contents

```
cv-observed-for-tdm.qmd     # the report
data/
  Summary_SEGID.csv                          # model segment volumes (run C48)
  seg_shp/WFv1000_Segments.*                 # model network shapefile (HPMS fields, route/milepost)
  RegionalBoundary.gpkg                      # WFRC/MAG regional boundary (for clipping CCS stations)
  UDOT_VehicleClassificationCounts/
    JKLP_Length_WFRC_2023_Sept_Nov.csv       # raw UDOT CCS vehicle-length classification counts
    SiteData.csv                             # CCS station locations/metadata
    Length_to_Class.xlsx                     # UDOT length-bin reference (not read by the qmd; kept for context)
  FHWA_VM4_2023_UrbanTruckPct.csv            # FHWA VM-4 statewide truck-share comparison data
  WFv1000_TAZ__DSUP.geojson                  # model super-districts (whole counties, or the model-area
                                              # slice of a county) -- Box Elder/Weber/Davis/Salt Lake/Utah
  HPMS_FULL_UT_2023.gpkg                     # FHWA's full statewide HPMS extract for Utah, 2023 (large;
                                              # gitignored -- fetched by scripts/fetch_hpms_full_ut_2023.py)
data_processed/
  CCS_Reclass_Ratio_2025_2003.csv                        # written by the qmd itself (reclass-ratio-export cell)
  HPMS_2023_VMT_by_SuperDistrict_FunctionalClass.csv     # written by scripts/build_hpms_vmt_by_county_facility.py
  HPMS_2023_VMT_by_County_FacilityType.png               # written by scripts/plot_hpms_vmt_by_county_facility.py
scripts/
  fetch_hpms_full_ut_2023.py                 # downloads data/HPMS_FULL_UT_2023.gpkg from geo.dot.gov (run manually)
  build_hpms_vmt_by_county_facility.py       # joins the HPMS extract to the super-districts, writes the
                                              # data_processed VMT-by-county-and-facility-type CSV (run manually)
  plot_hpms_vmt_by_county_facility.py        # charts that CSV (run manually)
```

The three `scripts/` are data-prep steps, not part of `quarto render` -- they hit an
external API and take a few minutes, so their output is cached as checked-in CSVs/
GeoPackages under `data/` and `data_processed/` and just read by the qmd.
`data/HPMS_FULL_UT_2023.gpkg` itself is gitignored (118MB, over GitHub's 100MB limit) --
re-run `scripts/fetch_hpms_full_ut_2023.py` after cloning to regenerate it. Re-run the
scripts only when refreshing that data (e.g. a newer HPMS year).

## Setup

Requires [Quarto](https://quarto.org) and a Python environment with:

```
pandas
numpy
geopandas
matplotlib
pyogrio        # or fiona -- geopandas' shapefile/gpkg reader
ipykernel
```

Register a Jupyter kernel matching the `jupyter:` field in the qmd's frontmatter
(currently `wftdm-docs`), or edit that field to match your own kernel name:

```
python -m ipykernel install --user --name wftdm-docs
```

Then render:

```
quarto render 4t-truckvalidation.qmd
```

All paths in the qmd are relative to this folder, so it can be moved/copied anywhere
without further changes.
