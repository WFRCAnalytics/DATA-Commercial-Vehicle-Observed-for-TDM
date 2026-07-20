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
```

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
