"""Build WPBA Phase 1 social analytics helper outputs from the stats workbook."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from . import metrics
    from .role_labels import add_role_labels
    from .visual_inputs import build_phase1_visual_inputs
except ImportError:  # pragma: no cover - supports direct script execution.
    import metrics  # type: ignore
    from role_labels import add_role_labels  # type: ignore
    from visual_inputs import build_phase1_visual_inputs  # type: ignore


SOURCE_SHEET = "team_player_stats_2026"
OUTPUT_TABLES = [
    "player_game_summary",
    "team_game_summary",
    "player_season_summary",
    "team_season_summary",
    "phase1_visual_inputs",
    "data_dictionary",
    "qa_checks",
]

RAW_STAT_COLS = [
    "team_score", "opponent_score", "minutes", "pts", "fg2m", "fg2a", "fg3m", "fg3a",
    "ftm", "fta", "fgm", "fga", "ast", "fouls", "tov", "reb", "oreb", "dreb",
    "blk", "stl", "usage_pct_source", "usage_pct_calc",
]

PLAYER_GAME_COLUMNS = [
    "season", "game_id", "game_date", "game_date_display", "matchup", "team", "opponent",
    "team_score", "opponent_score", "result", "player_number", "player_name", "starter",
    "role_group", "minutes", "pts", "reb", "oreb", "dreb", "ast", "tov", "stl", "blk",
    "fouls", "fgm", "fga", "fg2m", "fg2a", "fg3m", "fg3a", "ftm", "fta", "fg_pct",
    "fg2_pct", "fg3_pct", "ft_pct", "efg_pct", "ts_pct", "usage_pct", "ft_rate",
    "three_pt_rate", "two_pt_rate", "ast_tov_ratio", "ppsa", "pts_per36", "reb_per36",
    "ast_per36", "stl_per36", "blk_per36", "tov_per36", "fouls_per36",
    "impact_score_base", "efficiency_bonus", "impact_score",
]

TEAM_GAME_COLUMNS = [
    "season", "game_id", "game_date", "game_date_display", "team", "opponent", "team_score",
    "opponent_score", "result", "fgm", "fga", "fg2m", "fg2a", "fg3m", "fg3a", "ftm",
    "fta", "oreb", "dreb", "reb", "ast", "tov", "stl", "blk", "fouls", "team_minutes",
    "poss", "opp_poss", "fg_pct", "fg2_pct", "fg3_pct", "ft_pct", "efg_pct", "ts_pct",
    "tov_pct", "oreb_pct", "dreb_pct", "ft_rate", "three_pt_rate", "two_pt_rate",
    "assist_rate", "off_rating", "def_rating", "net_rating", "pace",
    "pts", "opp_oreb", "opp_dreb",
]

TEAM_SEASON_COLUMNS = [
    "season", "team", "games_played", "wins", "losses", "win_pct", "pts_for", "pts_against",
    "ppg", "opp_ppg", "score_margin_pg", "fgm", "fga", "fg2m", "fg2a", "fg3m", "fg3a",
    "ftm", "fta", "oreb", "dreb", "reb", "ast", "tov", "stl", "blk", "fouls", "poss",
    "fg_pct", "fg2_pct", "fg3_pct", "ft_pct", "efg_pct", "ts_pct", "tov_pct", "oreb_pct",
    "dreb_pct", "ft_rate", "three_pt_rate", "two_pt_rate", "assist_rate", "off_rating",
    "def_rating", "net_rating", "pace", "rank_ppg", "rank_opp_ppg", "rank_off_rating",
    "rank_def_rating", "rank_net_rating", "rank_efg_pct", "rank_tov_pct", "rank_oreb_pct",
    "rank_ft_rate",
]

PLAYER_SEASON_COLUMNS = [
    "season", "team", "player_name", "player_number", "games_played", "starts", "bench_games",
    "total_minutes", "mpg", "ppg", "rpg", "oreb_pg", "dreb_pg", "apg", "spg", "bpg",
    "tov_pg", "fouls_pg", "fgm", "fga", "fg2m", "fg2a", "fg3m", "fg3a", "ftm", "fta",
    "fg_pct", "fg2_pct", "fg3_pct", "ft_pct", "efg_pct", "ts_pct", "usage_pct",
    "ft_rate", "three_pt_rate", "two_pt_rate", "ast_tov_ratio", "ppsa", "pts_per36",
    "reb_per36", "ast_per36", "stl_per36", "blk_per36", "tov_per36", "fouls_per36",
    "avg_impact_score", "percentile_scoring", "percentile_efficiency", "percentile_playmaking",
    "percentile_rebounding", "percentile_defense", "percentile_rim_pressure",
    "percentile_spacing", "player_role_label", "watchability_score",
]


def normalize_column_name(name) -> str:
    text = str(name).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def clean_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    result = df.copy()
    result.columns = [normalize_column_name(c) for c in result.columns]
    blank_cols = [
        c for c in result.columns
        if not c or c.startswith("unnamed") or result[c].isna().all()
    ]
    result = result.drop(columns=blank_cols, errors="ignore")
    return result, len(blank_cols)


def normalize_dates(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    excel_dates = pd.to_datetime(numeric, unit="D", origin="1899-12-30", errors="coerce")
    parsed = pd.to_datetime(series, errors="coerce")
    return parsed.where(parsed.notna(), excel_dates).dt.normalize()


def normalize_starter(value) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return bool(value)
    text = str(value).strip().lower()
    return text in {"true", "yes", "y", "1", "starter"}


def load_source_workbook(input_path: Path) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], int]:
    workbook = pd.ExcelFile(input_path)
    if SOURCE_SHEET not in workbook.sheet_names:
        raise ValueError(f"Required sheet '{SOURCE_SHEET}' not found in {input_path}")

    source_raw = pd.read_excel(input_path, sheet_name=SOURCE_SHEET)
    source, removed_cols = clean_columns(source_raw)
    source["game_date"] = normalize_dates(source["game_date"])
    source["game_date_display"] = source["game_date"].dt.strftime("%b %-d, %Y")
    source["starter"] = source.get("starter", False).apply(normalize_starter)
    source["season"] = source["game_date"].dt.year.fillna(2026).astype(int)

    for col in RAW_STAT_COLS:
        if col in source.columns:
            source[col] = pd.to_numeric(source[col], errors="coerce")

    contexts = {}
    for sheet in workbook.sheet_names:
        if sheet == SOURCE_SHEET:
            continue
        ctx, _ = clean_columns(pd.read_excel(input_path, sheet_name=sheet))
        contexts[sheet] = ctx
    return source, contexts, removed_cols


def add_rate_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["fg_pct"] = metrics.calc_fg_pct(result["fgm"], result["fga"])
    result["fg2_pct"] = metrics.calc_fg2_pct(result["fg2m"], result["fg2a"])
    result["fg3_pct"] = metrics.calc_fg3_pct(result["fg3m"], result["fg3a"])
    result["ft_pct"] = metrics.calc_ft_pct(result["ftm"], result["fta"])
    result["efg_pct"] = metrics.calc_efg_pct(result["fgm"], result["fg3m"], result["fga"])
    result["ts_pct"] = metrics.calc_ts_pct(result["pts"], result["fga"], result["fta"])
    result["ft_rate"] = metrics.calc_ft_rate(result["fta"], result["fga"])
    result["three_pt_rate"] = metrics.calc_three_pt_rate(result["fg3a"], result["fga"])
    result["two_pt_rate"] = metrics.calc_two_pt_rate(result["fg2a"], result["fga"])
    result["ast_tov_ratio"] = metrics.calc_ast_tov_ratio(result["ast"], result["tov"])
    result["ppsa"] = metrics.calc_ppsa(result["pts"], result["fga"])
    return result


def build_player_game_summary(source: pd.DataFrame) -> pd.DataFrame:
    df = source.copy()
    for col in ["fgm", "fga", "fg2m", "fg2a", "fg3m", "fg3a", "ftm", "fta", "pts", "reb", "oreb", "dreb", "ast", "tov", "stl", "blk", "fouls", "minutes"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["result"] = np.select(
        [df["team_score"] > df["opponent_score"], df["team_score"] < df["opponent_score"]],
        ["W", "L"],
        default="",
    )
    df["role_group"] = np.where(df["starter"], "Starter", "Bench")
    df["usage_pct"] = df["usage_pct_calc"].combine_first(df["usage_pct_source"])
    df = add_rate_columns(df)

    for stat in ["pts", "reb", "ast", "stl", "blk", "tov", "fouls"]:
        df[f"{stat}_per36"] = metrics.calc_per36(df[stat], df["minutes"])

    team_ts = (
        df.groupby(["game_id", "team"], dropna=False)[["pts", "fga", "fta"]]
        .sum()
        .reset_index()
    )
    team_ts["team_ts_calc"] = metrics.calc_ts_pct(team_ts["pts"], team_ts["fga"], team_ts["fta"])
    df = df.merge(team_ts[["game_id", "team", "team_ts_calc"]], on=["game_id", "team"], how="left")

    df["impact_score_base"] = (
        df["pts"] + 1.2 * df["reb"] + 1.5 * df["ast"] + 3.0 * df["stl"]
        + 3.0 * df["blk"] - 1.5 * df["tov"]
    )
    df["efficiency_bonus"] = (10 * (df["ts_pct"] - df["team_ts_calc"])).fillna(0)
    df["impact_score"] = df["impact_score_base"] + df["efficiency_bonus"]

    return ensure_columns(df, PLAYER_GAME_COLUMNS)


def first_non_null(series: pd.Series):
    non_null = series.dropna()
    return non_null.iloc[0] if not non_null.empty else np.nan


def build_team_game_summary(player_game: pd.DataFrame) -> pd.DataFrame:
    stat_cols = ["pts", "fgm", "fga", "fg2m", "fg2a", "fg3m", "fg3a", "ftm", "fta", "oreb", "dreb", "reb", "ast", "tov", "stl", "blk", "fouls"]
    grouped = player_game.groupby(["season", "game_id", "team"], dropna=False)
    team = grouped.agg(
        game_date=("game_date", first_non_null),
        game_date_display=("game_date_display", first_non_null),
        opponent=("opponent", first_non_null),
        team_score=("team_score", first_non_null),
        opponent_score=("opponent_score", first_non_null),
        result=("result", first_non_null),
        team_minutes=("minutes", "sum"),
        **{col: (col, "sum") for col in stat_cols},
    ).reset_index()

    team["poss"] = metrics.calc_possessions(team["fga"], team["fta"], team["oreb"], team["tov"])
    team = add_rate_columns(team)

    opponent_ref = team[["game_id", "team", "poss", "oreb", "dreb", "team_score"]].rename(columns={
        "team": "opponent",
        "poss": "opp_poss",
        "oreb": "opp_oreb",
        "dreb": "opp_dreb",
        "team_score": "opp_pts_ref",
    })
    team = team.merge(opponent_ref, on=["game_id", "opponent"], how="left")

    team["tov_pct"] = metrics.calc_tov_pct(team["tov"], team["poss"])
    team["oreb_pct"] = metrics.calc_oreb_pct(team["oreb"], team["opp_dreb"])
    team["dreb_pct"] = metrics.calc_dreb_pct(team["dreb"], team["opp_oreb"])
    team["assist_rate"] = metrics.calc_assist_rate(team["ast"], team["fgm"])
    team["off_rating"] = metrics.calc_off_rating(team["team_score"], team["poss"])
    team["def_rating"] = metrics.calc_def_rating(team["opponent_score"], team["opp_poss"])
    team["net_rating"] = metrics.calc_net_rating(team["off_rating"], team["def_rating"])
    team["pace"] = metrics.calc_pace(team["poss"], team["team_minutes"])

    return ensure_columns(team, TEAM_GAME_COLUMNS)


def rank_series(series: pd.Series, ascending: bool) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").rank(method="min", ascending=ascending).astype("Int64")


def build_team_season_summary(team_game: pd.DataFrame) -> pd.DataFrame:
    complete = team_game[team_game["team_score"].notna() & team_game["opponent_score"].notna()].copy()
    stat_cols = ["fgm", "fga", "fg2m", "fg2a", "fg3m", "fg3a", "ftm", "fta", "oreb", "dreb", "reb", "ast", "tov", "stl", "blk", "fouls", "poss"]
    grouped = complete.groupby(["season", "team"], dropna=False)
    season = grouped.agg(
        games_played=("game_id", "nunique"),
        wins=("result", lambda s: (s == "W").sum()),
        losses=("result", lambda s: (s == "L").sum()),
        pts_for=("team_score", "sum"),
        pts_against=("opponent_score", "sum"),
        team_minutes=("team_minutes", "sum"),
        opp_poss=("opp_poss", "sum"),
        opp_oreb=("opp_oreb", "sum"),
        opp_dreb=("opp_dreb", "sum"),
        **{col: (col, "sum") for col in stat_cols},
    ).reset_index()

    season["win_pct"] = metrics.safe_div(season["wins"], season["games_played"])
    season["ppg"] = metrics.safe_div(season["pts_for"], season["games_played"])
    season["opp_ppg"] = metrics.safe_div(season["pts_against"], season["games_played"])
    season["score_margin_pg"] = season["ppg"] - season["opp_ppg"]
    season["pts"] = season["pts_for"]
    season = add_rate_columns(season)
    season["tov_pct"] = metrics.calc_tov_pct(season["tov"], season["poss"])
    season["oreb_pct"] = metrics.calc_oreb_pct(season["oreb"], season["opp_dreb"])
    season["dreb_pct"] = metrics.calc_dreb_pct(season["dreb"], season["opp_oreb"])
    season["assist_rate"] = metrics.calc_assist_rate(season["ast"], season["fgm"])
    season["off_rating"] = metrics.calc_off_rating(season["pts_for"], season["poss"])
    season["def_rating"] = metrics.calc_def_rating(season["pts_against"], season["opp_poss"])
    season["net_rating"] = metrics.calc_net_rating(season["off_rating"], season["def_rating"])
    season["pace"] = metrics.calc_pace(season["poss"], season["team_minutes"])

    season["rank_ppg"] = rank_series(season["ppg"], ascending=False)
    season["rank_opp_ppg"] = rank_series(season["opp_ppg"], ascending=True)
    season["rank_off_rating"] = rank_series(season["off_rating"], ascending=False)
    season["rank_def_rating"] = rank_series(season["def_rating"], ascending=True)
    season["rank_net_rating"] = rank_series(season["net_rating"], ascending=False)
    season["rank_efg_pct"] = rank_series(season["efg_pct"], ascending=False)
    season["rank_tov_pct"] = rank_series(season["tov_pct"], ascending=True)
    season["rank_oreb_pct"] = rank_series(season["oreb_pct"], ascending=False)
    season["rank_ft_rate"] = rank_series(season["ft_rate"], ascending=False)

    return ensure_columns(season, TEAM_SEASON_COLUMNS)


def percentile(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    return (values.rank(pct=True, method="average") * 100).round(1)


def build_player_season_summary(player_game: pd.DataFrame) -> pd.DataFrame:
    stat_cols = ["pts", "reb", "oreb", "dreb", "ast", "stl", "blk", "tov", "fouls", "fgm", "fga", "fg2m", "fg2a", "fg3m", "fg3a", "ftm", "fta"]
    pg = player_game.copy()
    pg["usage_weighted"] = pg["usage_pct"] * pg["minutes"]
    grouped = pg.groupby(["season", "team", "player_name"], dropna=False)
    season = grouped.agg(
        player_number=("player_number", first_non_null),
        games_played=("game_id", "nunique"),
        starts=("starter", "sum"),
        total_minutes=("minutes", "sum"),
        usage_weighted=("usage_weighted", "sum"),
        avg_impact_score=("impact_score", "mean"),
        **{col: (col, "sum") for col in stat_cols},
    ).reset_index()

    season["bench_games"] = season["games_played"] - season["starts"]
    season["usage_pct"] = metrics.safe_div(season["usage_weighted"], season["total_minutes"])
    for source, target in [
        ("total_minutes", "mpg"), ("pts", "ppg"), ("reb", "rpg"), ("oreb", "oreb_pg"),
        ("dreb", "dreb_pg"), ("ast", "apg"), ("stl", "spg"), ("blk", "bpg"),
        ("tov", "tov_pg"), ("fouls", "fouls_pg"),
    ]:
        denom = season["games_played"] if source != "total_minutes" else season["games_played"]
        season[target] = metrics.safe_div(season[source], denom)

    season = add_rate_columns(season)
    for stat in ["pts", "reb", "ast", "stl", "blk", "tov", "fouls"]:
        season[f"{stat}_per36"] = metrics.calc_per36(season[stat], season["total_minutes"])

    season["percentile_scoring"] = percentile(season["pts_per36"])
    season["percentile_efficiency"] = percentile(season["ts_pct"])
    season["percentile_playmaking"] = percentile(season["ast_per36"].fillna(0) + season["ast_tov_ratio"].fillna(0))
    season["percentile_rebounding"] = percentile(season["reb_per36"])
    season["percentile_defense"] = percentile(season["stl_per36"].fillna(0) + season["blk_per36"].fillna(0))
    season["percentile_rim_pressure"] = (
        percentile(season["ft_rate"]).fillna(0) + percentile(season["two_pt_rate"]).fillna(0)
    ) / 2
    season["percentile_spacing"] = (
        percentile(season["three_pt_rate"]).fillna(0) + percentile(season["fg3_pct"]).fillna(0)
    ) / 2
    season = add_role_labels(season)
    impact_percentile = percentile(season["avg_impact_score"]).fillna(0)
    season["watchability_score"] = (
        0.25 * season["percentile_scoring"].fillna(0)
        + 0.20 * season["percentile_efficiency"].fillna(0)
        + 0.20 * season[["percentile_rebounding", "percentile_spacing", "percentile_rim_pressure"]].fillna(0).max(axis=1)
        + 0.20 * season[["percentile_playmaking", "percentile_defense"]].fillna(0).max(axis=1)
        + 0.15 * impact_percentile
    ).round(1)

    return ensure_columns(season, PLAYER_SEASON_COLUMNS)


def build_data_dictionary() -> pd.DataFrame:
    rows = []
    definitions = {
        "fg_pct": ("number", "Field goal percentage", "FGM / FGA"),
        "efg_pct": ("number", "Effective field goal percentage", "(FGM + 0.5 * 3PM) / FGA"),
        "ts_pct": ("number", "True shooting percentage", "PTS / (2 * (FGA + 0.44 * FTA))"),
        "poss": ("number", "Estimated possessions", "FGA + 0.44 * FTA - OREB + TOV"),
        "off_rating": ("number", "Points per 100 possessions", "100 * PTS / possessions"),
        "def_rating": ("number", "Opponent points per 100 possessions", "100 * opponent PTS / opponent possessions"),
        "net_rating": ("number", "Offensive rating minus defensive rating", "off_rating - def_rating"),
        "watchability_score": ("number", "0-100 fan-facing player composite", "Weighted percentile blend"),
        "impact_score": ("number", "Player game impact composite", "PTS + 1.2*REB + 1.5*AST + 3*STL + 3*BLK - 1.5*TOV + efficiency bonus"),
    }
    for table_name, columns in {
        "player_game_summary": PLAYER_GAME_COLUMNS,
        "team_game_summary": TEAM_GAME_COLUMNS,
        "player_season_summary": PLAYER_SEASON_COLUMNS,
        "team_season_summary": TEAM_SEASON_COLUMNS,
    }.items():
        for field in columns:
            field_type, definition, formula = definitions.get(field, ("mixed", f"{field} output field", ""))
            rows.append({
                "table_name": table_name,
                "field_name": field,
                "field_type": field_type,
                "definition": definition,
                "formula": formula,
                "source_table": SOURCE_SHEET,
                "notes": "",
            })
    for note in [
        "No play-by-play yet.",
        "No shot location or shot zone data yet.",
        "No quarter scores unless another source is added.",
        "No player position column yet.",
        "No player photo URLs yet.",
        "No lineup/on-off data yet.",
        "Clutch and turning point templates require play-by-play later.",
        "Pressure Points and Shot Diet templates require shot zone/location data later.",
        "Percentiles are currently league-wide, not position-adjusted.",
        "Two weeks of data means small-sample volatility is high.",
    ]:
        rows.append({
            "table_name": "known_limitations",
            "field_name": "",
            "field_type": "note",
            "definition": note,
            "formula": "",
            "source_table": "",
            "notes": note,
        })
    return pd.DataFrame(rows)


def qa_row(name: str, status: str, details: str) -> dict[str, str]:
    return {"check_name": name, "status": status, "details": details}


def build_qa_checks(source: pd.DataFrame, player_game: pd.DataFrame, team_game: pd.DataFrame, player_season: pd.DataFrame, removed_cols: int) -> pd.DataFrame:
    rows = []
    rows.append(qa_row("source_rows_loaded", "pass" if len(source) > 0 else "fail", f"{len(source)} source rows loaded"))
    rows.append(qa_row("blank_unnamed_columns_removed", "pass", f"{removed_cols} blank/unnamed columns removed"))
    numeric_bad = sum(source[col].dtype == object for col in RAW_STAT_COLS if col in source.columns)
    rows.append(qa_row("numeric_coercion_completed", "pass" if numeric_bad == 0 else "warn", f"{numeric_bad} configured numeric columns remain object dtype"))
    dupes = int(player_game.duplicated(["game_id", "team", "player_name"]).sum())
    rows.append(qa_row("duplicate_player_game_rows", "pass" if dupes == 0 else "warn", f"{dupes} duplicate player-game rows"))
    unique_team_games = source[["game_id", "team"]].drop_duplicates().shape[0]
    rows.append(qa_row("team_game_row_count", "pass" if len(team_game) == unique_team_games else "warn", f"{len(team_game)} team-game rows; {unique_team_games} unique source team-games"))
    score_mismatches = int((team_game["team_score"].round(6) != team_game.groupby(["game_id", "team"])["team_score"].transform("first").round(6)).sum())
    rows.append(qa_row("team_score_metadata_consistency", "pass" if score_mismatches == 0 else "warn", f"{score_mismatches} score metadata mismatches"))
    point_mismatches = int((team_game["pts"].round(6) != team_game["team_score"].round(6)).sum())
    rows.append(qa_row("team_points_sum_equals_team_score", "pass" if point_mismatches == 0 else "warn", f"{point_mismatches} team rows where player points do not equal team_score"))
    neg_poss = int((team_game["poss"] < 0).sum())
    rows.append(qa_row("possessions_non_negative", "pass" if neg_poss == 0 else "warn", f"{neg_poss} negative possession rows"))
    inf_count = count_infinite([player_game, team_game, player_season])
    rows.append(qa_row("no_infinite_values", "pass" if inf_count == 0 else "warn", f"{inf_count} infinite values found"))
    pct_cols = [c for c in player_season.columns if c.startswith("percentile_")]
    pct_bad = int((~player_season[pct_cols].apply(lambda s: s.between(0, 100) | s.isna())).sum().sum()) if pct_cols else 0
    rows.append(qa_row("percentiles_between_0_and_100", "pass" if pct_bad == 0 else "warn", f"{pct_bad} percentile values outside 0-100"))
    season_incomplete = int(team_game[team_game["team_score"].isna() | team_game["opponent_score"].isna()].shape[0])
    rows.append(qa_row("completed_games_only_in_season_summaries", "pass", f"{season_incomplete} unscored team-game rows excluded"))
    missing_opponents = int(team_game["opp_poss"].isna().sum())
    rows.append(qa_row("missing_opponent_row_count", "pass" if missing_opponents == 0 else "warn", f"{missing_opponents} team-game rows missing an opponent row"))
    return pd.DataFrame(rows)


def count_infinite(frames: list[pd.DataFrame]) -> int:
    total = 0
    for frame in frames:
        numeric = frame.select_dtypes(include=[np.number])
        if not numeric.empty:
            total += int(np.isinf(numeric.to_numpy()).sum())
    return total


def ensure_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    result = df.copy()
    for col in columns:
        if col not in result.columns:
            result[col] = np.nan
    return result[columns].replace([np.inf, -np.inf], np.nan)


def write_outputs(outputs: dict[str, pd.DataFrame], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_TABLES:
        outputs[name].to_csv(output_dir / f"{name}.csv", index=False)
    with pd.ExcelWriter(output_dir / "wpba_phase1_helper_outputs.xlsx", engine="openpyxl") as writer:
        for name in OUTPUT_TABLES:
            outputs[name].to_excel(writer, sheet_name=name[:31], index=False)


def run_pipeline(input_path: str | Path, output_dir: str | Path) -> dict[str, pd.DataFrame]:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    source, _contexts, removed_cols = load_source_workbook(input_path)
    player_game = build_player_game_summary(source)
    team_game = build_team_game_summary(player_game)
    team_season = build_team_season_summary(team_game)
    player_season = build_player_season_summary(player_game)
    visual_inputs = build_phase1_visual_inputs()
    data_dictionary = build_data_dictionary()
    qa_checks = build_qa_checks(source, player_game, team_game, player_season, removed_cols)

    outputs = {
        "source_clean": source,
        "player_game_summary": player_game,
        "team_game_summary": team_game,
        "player_season_summary": player_season,
        "team_season_summary": team_season,
        "phase1_visual_inputs": visual_inputs,
        "data_dictionary": data_dictionary,
        "qa_checks": qa_checks,
    }
    write_outputs(outputs, output_dir)
    return outputs


def print_qa_summary(outputs: dict[str, pd.DataFrame], output_dir: Path) -> None:
    print("WPBA Phase 1 helper outputs generated")
    for name in OUTPUT_TABLES:
        print(f"- {name}.csv: {len(outputs[name])} rows")
    warn_count = int((outputs["qa_checks"]["status"] != "pass").sum())
    print(f"QA warnings: {warn_count}")
    print(f"Output folder: {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build WPBA Phase 1 social analytics helper tables.")
    parser.add_argument("--input", required=True, help="Path to the WPBA stats workbook.")
    parser.add_argument("--output-dir", default="outputs", help="Folder for generated CSV and helper workbook outputs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    outputs = run_pipeline(args.input, output_dir)
    print_qa_summary(outputs, output_dir)


if __name__ == "__main__":
    main()
