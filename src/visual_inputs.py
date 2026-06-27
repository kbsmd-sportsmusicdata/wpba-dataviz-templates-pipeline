"""Phase 1 visual-template mapping for WPBA social analytics outputs."""

from __future__ import annotations

import pandas as pd


VISUAL_ROWS = [
    {
        "visual_name": "Matchup Overview",
        "use_case": "Pre-game matchup preview",
        "primary_source_table": "team_season_summary",
        "secondary_source_table": "team_game_summarys",
        "required_fields": "team, opponent, record, ppg, opp_ppg, off_rating, def_rating, net_rating, pace, ranks",
        "available_now": "Yes",
        "missing_fields": "Upcoming schedule rows only if absent from source workbook",
        "build_readiness": "Ready",
        "recommended_chart_type": "KPI cards + team comparison bars",
        "notes": "Use calculated season summaries as the metric source of truth.",
    },
    {
        "visual_name": "Four Factors Tug-of-War",
        "use_case": "Pre-game strengths comparison",
        "primary_source_table": "team_season_summary",
        "secondary_source_table": "",
        "required_fields": "efg_pct, tov_pct, oreb_pct, ft_rate",
        "available_now": "Yes",
        "missing_fields": "",
        "build_readiness": "Ready",
        "recommended_chart_type": "Diverging bars",
        "notes": "Higher eFG%, OREB%, and FT rate are positive; lower TOV% is positive.",
    },
    {
        "visual_name": "Since Last Meeting",
        "use_case": "Pre-game rematch context",
        "primary_source_table": "team_game_summary",
        "secondary_source_table": "team_season_summary",
        "required_fields": "prior head-to-head games, current form, ppg, efg_pct, tov_pct, oreb_pct, ft_rate, net_rating",
        "available_now": "Partial",
        "missing_fields": "Longer game history and standings trend context",
        "build_readiness": "Fallback Ready",
        "recommended_chart_type": "Delta cards or slopegraph",
        "notes": "Fallback copy: Since Opening Weekend or Last 4 Games Trend.",
    },
    {
        "visual_name": "Why You Should Watch",
        "use_case": "Player-led preview card",
        "primary_source_table": "player_season_summary",
        "secondary_source_table": "",
        "required_fields": "player_name, team, ppg, rpg, apg, ts_pct, usage_pct, percentiles, role label, watchability_score",
        "available_now": "Yes",
        "missing_fields": "Player photos",
        "build_readiness": "Ready",
        "recommended_chart_type": "Player card + percentile bars",
        "notes": "Use watchability_score to choose featured players.",
    },
    {
        "visual_name": "Final Score",
        "use_case": "Post-game recap",
        "primary_source_table": "team_game_summary",
        "secondary_source_table": "player_game_summary",
        "required_fields": "team, opponent, team_score, opponent_score, result, top performers",
        "available_now": "Yes",
        "missing_fields": "",
        "build_readiness": "Ready",
        "recommended_chart_type": "Score card + top performers",
        "notes": "Top performers can be selected by impact_score.",
    },
    {
        "visual_name": "How They Won",
        "use_case": "Post-game evidence recap",
        "primary_source_table": "team_game_summary",
        "secondary_source_table": "",
        "required_fields": "four factor edges, rebound edge, assist edge, defensive event edge",
        "available_now": "Yes",
        "missing_fields": "",
        "build_readiness": "Ready",
        "recommended_chart_type": "Evidence tiles / edge cards",
        "notes": "Compare each team row against its opponent row from the same game.",
    },
    {
        "visual_name": "Player of the Game",
        "use_case": "Post-game player spotlight",
        "primary_source_table": "player_game_summary",
        "secondary_source_table": "",
        "required_fields": "impact_score, pts, reb, ast, stl, blk, ts_pct, usage_pct",
        "available_now": "Yes",
        "missing_fields": "Player photos",
        "build_readiness": "Ready",
        "recommended_chart_type": "Player stat card + impact badge",
        "notes": "Rank by impact_score within a completed game.",
    },
    {
        "visual_name": "Team Edge Recap",
        "use_case": "Post-game stat edge recap",
        "primary_source_table": "team_game_summary",
        "secondary_source_table": "",
        "required_fields": "stat edges across shooting, glass, turnovers, assists, steals, blocks, FT rate",
        "available_now": "Yes",
        "missing_fields": "",
        "build_readiness": "Ready",
        "recommended_chart_type": "Stat edge grid",
        "notes": "Use paired game rows to calculate edges.",
    },
]


def build_phase1_visual_inputs() -> pd.DataFrame:
    return pd.DataFrame(VISUAL_ROWS)
