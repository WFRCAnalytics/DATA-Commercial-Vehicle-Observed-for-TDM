"""Chart 2023 HPMS truck VMT by super-district (county) and facility type.

Reads data_processed/HPMS_2023_VMT_by_SuperDistrict_FunctionalClass.csv (see
scripts/build_hpms_vmt_by_county_facility.py) and saves a grouped-bar chart
comparing Medium and Heavy truck VMT across counties, one panel per truck type.

Local is excluded from the chart -- its VMT is negligible next to the other
facility types and mostly just adds visual clutter (it still shows up in the
underlying CSV and in the qmd's county-toggle table).

Run manually:
    python scripts/plot_hpms_vmt_by_county_facility.py

Writes data_processed/HPMS_2023_VMT_by_County_FacilityType.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

FT_ORDER = ["Freeway", "Expressway", "Principal Arterial", "Minor Arterial", "Collector"]
DSUP_ORDER = ["Box Elder County", "Weber County", "Davis County", "Salt Lake County", "Utah County"]
DSUP_COLORS = {
    "Box Elder County": "#2a78d6",
    "Weber County": "#7b52ab",
    "Davis County": "#008300",
    "Salt Lake County": "#e87ba4",
    "Utah County": "#eda100",
}

DATA_PROCESSED = "data_processed"
IN_CSV = f"{DATA_PROCESSED}/HPMS_2023_VMT_by_SuperDistrict_FunctionalClass.csv"
OUT_PNG = f"{DATA_PROCESSED}/HPMS_2023_VMT_by_County_FacilityType.png"


def style_axes(ax):
    ax.set_facecolor("#fcfcfb")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#c3c2b7")
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors="#52514e", labelsize=9)
    ax.yaxis.grid(True, color="#e1e0d9", linewidth=1, zorder=0)
    ax.set_axisbelow(True)


def main():
    hpms = pd.read_csv(IN_CSV)
    hpms = hpms[hpms["Functional Class"].isin(FT_ORDER)].copy()
    hpms["Functional Class"] = pd.Categorical(hpms["Functional Class"], categories=FT_ORDER, ordered=True)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), dpi=100)
    fig.patch.set_facecolor("#fcfcfb")

    x = np.arange(len(FT_ORDER))
    bar_width = 0.8 / len(DSUP_ORDER)

    for ax, col, title in zip(axes, ["MD", "HV"], ["Medium (Single-Unit) Truck VMT", "Heavy (Combination) Truck VMT"]):
        for i, dsup in enumerate(DSUP_ORDER):
            sub = hpms[hpms["DSUP_NAME"] == dsup].set_index("Functional Class").reindex(FT_ORDER)
            vals = sub[col].values
            offset = (i - (len(DSUP_ORDER) - 1) / 2) * bar_width
            ax.bar(
                x + offset, vals, width=bar_width * 0.9,
                color=DSUP_COLORS[dsup], label=dsup.replace(" County", ""),
            )
        ax.set_xticks(x)
        ax.set_xticklabels(FT_ORDER, rotation=25, ha="right", fontsize=9)
        ax.set_ylabel("Daily VMT", fontsize=9, color="#52514e")
        ax.set_title(title, fontsize=11, color="#0b0b0b", pad=10)
        style_axes(ax)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1.06), frameon=False, fontsize=9)
    fig.suptitle("2023 HPMS Truck VMT by Super-District and Facility Type", fontsize=13, y=1.14)
    plt.tight_layout()
    plt.savefig(OUT_PNG, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Saved chart to {OUT_PNG}")


if __name__ == "__main__":
    main()
