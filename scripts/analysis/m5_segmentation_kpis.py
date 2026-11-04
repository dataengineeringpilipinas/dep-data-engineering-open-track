#!/usr/bin/env python3
"""Phase 5 (Path B): segmentation, KPI framework and review shortlist.

Run from the repository root:
    python scripts/analysis/m5_segmentation_kpis.py

Input : data/processed/dpwh_flood_control_analysis_ready.csv
Output: data/processed/m5_*.csv  and  output/figures/m5_*.png

The notebook notebooks/M5_segmentation_kpis_brief.ipynb imports the functions below,
so the script and the notebook always show the same numbers.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INPUT_FILE = Path("data/processed/dpwh_flood_control_analysis_ready.csv")
PROCESSED_DIR = Path("data/processed")
FIGURE_DIR = Path("output/figures")
COST = "contract_cost_php"
MIN_PROJECTS = 30  # provinces below this give noisy concentration figures
MIN_QUARTER_PROJECTS = 100  # quarters below this are flagged as low volume

plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25})


# ---------------------------------------------------------------- preparation
def load(path: Path = INPUT_FILE) -> pd.DataFrame:
    return pd.read_csv(path)


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Add completion year/quarter, project-type group, over-budget flag and a
    time-adjusted outlier flag (z-score within region AND completion year)."""
    d = df.copy()
    done = pd.to_datetime(d["actualcompletiondate"], errors="coerce")
    d["completion_year"] = done.dt.year
    d["completion_quarter"] = done.dt.to_period("Q").astype(str)
    work = d["typeofwork"].str.replace("Construction of ", "", regex=False)
    d["work_group"] = work.where(work.isin(work.value_counts().head(4).index), "Other")
    budget = pd.to_numeric(d["approvedbudgetforcontract"], errors="coerce")
    d["over_budget"] = (d[COST] > budget).where(budget.notna())
    # Same cut-off as the original flag, but benchmarked within region x completion year
    cutoff = d.loc[d["is_high_cost_outlier"] == 1, "cost_zscore_regional"].min()
    grp = d.groupby(["region", "completion_year"])[COST]
    z = (d[COST] - grp.transform("mean")) / grp.transform("std")
    d["cost_zscore_region_year"] = z
    d["is_outlier_time_adjusted"] = (z >= cutoff).astype(int)
    return d


# ------------------------------------------------------------- Week 17: segments
def segment_island_year(d: pd.DataFrame) -> pd.DataFrame:
    return (d.groupby(["mainisland", "completion_year"])
            .agg(projects=("project_id", "count"), avg_cost_php_m=(COST, lambda s: s.mean() / 1e6),
                 outlier_rate=("is_high_cost_outlier", "mean"),
                 outlier_rate_time_adjusted=("is_outlier_time_adjusted", "mean"))
            .reset_index())


def segment_work_island(d: pd.DataFrame) -> pd.DataFrame:
    return (d.groupby(["work_group", "mainisland"])
            .agg(projects=("project_id", "count"), avg_cost_php_m=(COST, lambda s: s.mean() / 1e6),
                 outlier_rate=("is_high_cost_outlier", "mean")).reset_index())


def segment_contractor_tier(d: pd.DataFrame) -> pd.DataFrame:
    c = d.groupby("contractor").agg(projects=("project_id", "count"), value=(COST, "sum"))
    c["tier"] = pd.cut(c.projects, [0, 1, 5, 20, np.inf], labels=["1 project", "2-5", "6-20", "21+"])
    t = c.groupby("tier", observed=True).agg(contractors=("projects", "size"), projects=("projects", "sum"),
                                              value=("value", "sum")).reset_index()
    t["share_of_projects"] = t.projects / t.projects.sum()
    t["share_of_value"] = t.value / t.value.sum()
    return t


# --------------------------------------------------------------- Week 18: KPIs
def province_concentration(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for p, g in d.groupby("province"):
        s = g.groupby("contractor")[COST].sum().sort_values(ascending=False)
        if s.sum() <= 0:
            continue
        rows.append({"province": p, "region": g["region"].mode()[0], "projects": len(g),
                     "contractors": g["contractor"].nunique(), "top1_share": s.iloc[0] / s.sum(),
                     "top3_share": s.head(3).sum() / s.sum(), "outlier_rate": g["is_high_cost_outlier"].mean(),
                     "outlier_rate_time_adjusted": g["is_outlier_time_adjusted"].mean()})
    return pd.DataFrame(rows).sort_values("top1_share", ascending=False)


def kpi_quarterly(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for q, g in d.groupby("completion_quarter"):
        v = g.groupby("contractor")[COST].sum().sort_values(ascending=False)
        rows.append({"quarter": q, "projects": len(g),
                     "kpi1_outlier_rate": g["is_high_cost_outlier"].mean(),
                     "kpi1b_outlier_rate_time_adjusted": g["is_outlier_time_adjusted"].mean(),
                     "kpi2_avg_cost_php_m": g[COST].mean() / 1e6,
                     "kpi3_top10_contractor_share": v.head(10).sum() / v.sum(),
                     "kpi5_over_budget_rate": g["over_budget"].mean(),
                     "low_volume": len(g) < MIN_QUARTER_PROJECTS})
    return pd.DataFrame(rows)


def kpi_summary(d: pd.DataFrame, prov: pd.DataFrame) -> pd.DataFrame:
    big = prov[prov.projects >= MIN_PROJECTS]
    v = d.groupby("contractor")[COST].sum().sort_values(ascending=False)
    return pd.DataFrame([
        ["KPI 1", "High-cost outlier rate", d["is_high_cost_outlier"].mean(), "share of projects"],
        ["KPI 2", "Average contract cost (PHP M)", d[COST].mean() / 1e6, "PHP millions"],
        ["KPI 3", "Top-10 contractor share of value", v.head(10).sum() / v.sum(), "share of value"],
        ["KPI 4", f"Median provincial top-contractor share ({len(big)} provinces, {MIN_PROJECTS}+ projects)",
         big.top1_share.median(), "share of province value"],
        ["KPI 5", "Over-budget rate", d["over_budget"].mean(), "share of projects with a budget"],
    ], columns=["kpi", "name", "value", "unit"])


def review_shortlist(prov: pd.DataFrame) -> pd.DataFrame:
    big = prov[prov.projects >= MIN_PROJECTS]
    hi_conc = big.top1_share >= big.top1_share.quantile(.75)
    hi_flag = big.outlier_rate_time_adjusted > big.outlier_rate_time_adjusted.median()
    out = big[hi_conc & hi_flag].copy()
    out["reason"] = "Top-quartile contractor concentration and above-median time-adjusted outlier rate"
    return out.sort_values("top1_share", ascending=False)


# --------------------------------------------------------------------- figures
def fig_island_year(seg: pd.DataFrame):
    pv = seg.pivot(index="mainisland", columns="completion_year", values="outlier_rate") * 100
    cnt = seg.pivot(index="mainisland", columns="completion_year", values="projects")
    fig, ax = plt.subplots(figsize=(8, 3.8)); im = ax.imshow(pv.values, cmap="Oranges")
    ax.set_xticks(range(len(pv.columns)), pv.columns); ax.set_yticks(range(len(pv.index)), pv.index); ax.grid(False)
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            ax.text(j, i, f"{pv.values[i, j]:.1f}%\n(n={int(cnt.values[i, j])})", ha="center", va="center", fontsize=9)
    ax.set(title="Chart 6. High-cost outlier rate by island group and completion year", xlabel="Completion year")
    fig.colorbar(im, ax=ax, label="Flagged projects (%)"); fig.tight_layout(); return fig


def fig_contractor_tier(t: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4)); x = np.arange(len(t)); w = .38
    ax.bar(x - w / 2, t.share_of_projects * 100, w, label="Share of projects", color="#1F6FEB")
    ax.bar(x + w / 2, t.share_of_value * 100, w, label="Share of contract value", color="#0F766E")
    for i, n in enumerate(t.contractors): ax.text(i, 1, f"{n:,} contractors", ha="center", fontsize=8, color="white")
    ax.set_xticks(x, t.tier.astype(str)); ax.set(title="Chart 7. Contractor size tiers: share of projects and value",
                                                  xlabel="Projects won by the contractor", ylabel="Share (%)"); ax.legend()
    fig.tight_layout(); return fig


def fig_kpi_trends(k: pd.DataFrame):
    fig, ax = plt.subplots(2, 2, figsize=(12, 7), sharex=True); x = k.quarter
    panels = [("kpi1_outlier_rate", "KPI 1. High-cost outlier rate", 100, "%"),
              ("kpi2_avg_cost_php_m", "KPI 2. Average contract cost", 1, "PHP millions"),
              ("kpi3_top10_contractor_share", "KPI 3. Top-10 contractor share of value", 100, "%"),
              ("kpi5_over_budget_rate", "KPI 5. Over-budget rate", 100, "%")]
    for a, (c, title, m, unit) in zip(ax.ravel(), panels):
        a.plot(x, k[c] * m, marker="o", color="#1F6FEB")
        if c == "kpi1_outlier_rate": a.plot(x, k.kpi1b_outlier_rate_time_adjusted * 100, marker="s", ls="--", color="#B45309", label="Time-adjusted"); a.legend()
        low = k.low_volume.values
        a.scatter(x[low], (k[c] * m)[low], s=120, facecolors="none", edgecolors="red", label="Low volume (<100 projects)")
        a.set(title=title, ylabel=unit); a.tick_params(axis="x", rotation=60)
    ax[0, 0].legend(fontsize=8); fig.suptitle("Chart 8. KPI trends by completion quarter (red circle = low-volume quarter)", y=1.0)
    fig.tight_layout(); return fig


def fig_shortlist(prov: pd.DataFrame, short: pd.DataFrame):
    big = prov[prov.projects >= MIN_PROJECTS]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.scatter(big.top1_share * 100, big.outlier_rate_time_adjusted * 100, s=40, alpha=.6, color="#8A9BB5", label="Other provinces")
    ax.scatter(short.top1_share * 100, short.outlier_rate_time_adjusted * 100, s=60, color="#B45309", label="Review shortlist")
    for _, r in short.iterrows(): ax.annotate(r.province, (r.top1_share * 100, r.outlier_rate_time_adjusted * 100), fontsize=8, xytext=(4, 3), textcoords="offset points")
    ax.axvline(big.top1_share.quantile(.75) * 100, ls=":", color="grey"); ax.axhline(big.outlier_rate_time_adjusted.median() * 100, ls=":", color="grey")
    ax.set(title="Chart 9. Review shortlist: concentration vs time-adjusted outlier rate", xlabel="Top contractor share of province value (%)",
           ylabel="Time-adjusted outlier rate (%)"); ax.legend(); fig.tight_layout(); return fig


# ------------------------------------------------------------------------ main
def main() -> None:
    plt.switch_backend("Agg")  # headless when run as a script; notebooks keep their inline backend
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True); FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    d = prepare(load())
    prov = province_concentration(d); k = kpi_quarterly(d); short = review_shortlist(prov)
    seg1, seg2, seg3 = segment_island_year(d), segment_work_island(d), segment_contractor_tier(d)
    outputs = {"m5_segment_island_year.csv": seg1, "m5_segment_work_island.csv": seg2, "m5_segment_contractor_tier.csv": seg3,
               "m5_province_concentration.csv": prov, "m5_kpi_quarterly.csv": k, "m5_kpi_summary.csv": kpi_summary(d, prov),
               "m5_review_shortlist.csv": short}
    for name, frame in outputs.items(): frame.round(4).to_csv(PROCESSED_DIR / name, index=False)
    for name, fig in {"m5_chart6_island_year.png": fig_island_year(seg1), "m5_chart7_contractor_tiers.png": fig_contractor_tier(seg3),
                      "m5_chart8_kpi_trends.png": fig_kpi_trends(k), "m5_chart9_review_shortlist.png": fig_shortlist(prov, short)}.items():
        fig.savefig(FIGURE_DIR / name, bbox_inches="tight"); plt.close(fig)
    print(f"Wrote {len(outputs)} tables to {PROCESSED_DIR}/ and 4 figures to {FIGURE_DIR}/")
    print(outputs["m5_kpi_summary.csv"].round(3).to_string(index=False))
    print(f"Review shortlist: {len(short)} provinces")


if __name__ == "__main__":
    main()
