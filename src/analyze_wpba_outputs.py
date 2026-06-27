"""Create first-pass analysis summaries from processed WPBA helper outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TEAM_METRICS = [
    ("ppg", False, "points per game"),
    ("opp_ppg", True, "opponent points per game"),
    ("score_margin_pg", False, "score margin per game"),
    ("off_rating", False, "offensive rating"),
    ("def_rating", True, "defensive rating"),
    ("net_rating", False, "net rating"),
    ("efg_pct", False, "effective field goal percentage"),
    ("ts_pct", False, "true shooting percentage"),
    ("tov_pct", True, "turnover rate"),
    ("oreb_pct", False, "offensive rebound rate"),
    ("dreb_pct", False, "defensive rebound rate"),
    ("ft_rate", False, "free throw rate"),
    ("three_pt_rate", False, "three point attempt rate"),
    ("pace", False, "pace"),
]

PLAYER_METRICS = [
    ("ppg", False, "points per game"),
    ("rpg", False, "rebounds per game"),
    ("apg", False, "assists per game"),
    ("ts_pct", False, "true shooting percentage"),
    ("usage_pct", False, "usage percentage"),
    ("pts_per36", False, "points per 36"),
    ("reb_per36", False, "rebounds per 36"),
    ("ast_per36", False, "assists per 36"),
    ("stl_per36", False, "steals per 36"),
    ("blk_per36", False, "blocks per 36"),
    ("avg_impact_score", False, "average impact score"),
    ("watchability_score", False, "watchability score"),
]

DEFAULT_MIN_PLAYER_MINUTES = 40


def build_metric_leaders(
    df: pd.DataFrame,
    entity_col: str,
    metrics: list[tuple[str, bool, str]],
    top_n: int,
) -> pd.DataFrame:
    rows = []
    for metric, ascending, label in metrics:
        if metric not in df.columns:
            continue
        metric_df = df[[entity_col, metric]].copy()
        metric_df[metric] = pd.to_numeric(metric_df[metric], errors="coerce")
        metric_df = metric_df.dropna(subset=[metric])
        if metric_df.empty:
            continue
        ranked = metric_df.sort_values(metric, ascending=ascending).head(top_n)
        for rank, row in enumerate(ranked.itertuples(index=False), start=1):
            rows.append({
                "metric": metric,
                "metric_label": label,
                "rank": rank,
                "leader": getattr(row, entity_col),
                "value": getattr(row, metric),
                "sort_direction": "ascending" if ascending else "descending",
            })
    return pd.DataFrame(rows)


def build_analysis_summary(team_leaders: pd.DataFrame, player_leaders: pd.DataFrame) -> str:
    lines = [
        "# WPBA Processed Dataset Analysis",
        "",
        "This report is generated from the processed player and team summary datasets.",
        "",
        "## Team Signals",
    ]
    for row in team_leaders[team_leaders["rank"] == 1].itertuples(index=False):
        lines.append(f"- {row.metric_label}: {row.leader} ({row.value:.3f})")

    lines.extend(["", "## Player Signals"])
    for row in player_leaders[player_leaders["rank"] == 1].itertuples(index=False):
        lines.append(f"- {row.metric_label}: {row.leader} ({row.value:.3f})")

    lines.extend([
        "",
        "## Suggested Next Review",
        "- Compare team strengths against the Phase 1 visual readiness map.",
        "- Pick visuals after reviewing which team/player signals are strongest.",
        "- Treat small samples cautiously until more games are added.",
        "",
    ])
    return "\n".join(lines)


def filter_player_analysis_pool(player_season: pd.DataFrame, min_minutes: float) -> pd.DataFrame:
    if "total_minutes" not in player_season.columns:
        return player_season
    result = player_season.copy()
    result["total_minutes"] = pd.to_numeric(result["total_minutes"], errors="coerce")
    return result[result["total_minutes"] >= min_minutes].copy()


def run_analysis(
    input_dir: Path,
    output_dir: Path,
    top_n: int = 3,
    min_player_minutes: float = DEFAULT_MIN_PLAYER_MINUTES,
) -> dict[str, Path]:
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    team_season = pd.read_csv(input_dir / "team_season_summary.csv")
    player_season = pd.read_csv(input_dir / "player_season_summary.csv")
    player_pool = filter_player_analysis_pool(player_season, min_player_minutes)

    team_leaders = build_metric_leaders(team_season, "team", TEAM_METRICS, top_n)
    player_leaders = build_metric_leaders(player_pool, "player_name", PLAYER_METRICS, top_n)
    summary = build_analysis_summary(team_leaders, player_leaders)

    paths = {
        "team_metric_leaders": output_dir / "team_metric_leaders.csv",
        "player_metric_leaders": output_dir / "player_metric_leaders.csv",
        "analysis_summary": output_dir / "analysis_summary.md",
    }
    team_leaders.to_csv(paths["team_metric_leaders"], index=False)
    player_leaders.to_csv(paths["player_metric_leaders"], index=False)
    paths["analysis_summary"].write_text(summary)
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis"))
    parser.add_argument("--top-n", type=int, default=3)
    parser.add_argument("--min-player-minutes", type=float, default=DEFAULT_MIN_PLAYER_MINUTES)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = run_analysis(args.input_dir, args.output_dir, args.top_n, args.min_player_minutes)
    print("WPBA analysis outputs generated")
    for name, path in paths.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
