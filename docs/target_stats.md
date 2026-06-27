# Target Stats And Calculated Metrics

This repo is designed to produce analysis-ready player and team datasets before any visual template work begins.

## Source Cleaning Targets

The pipeline reads `data/wpba_stats_2026_clean.xlsx`.

Required source sheet:

- `team_player_stats_2026`

Optional context sheets:

- `team_game_summarys`
- `team_season_summary`

Cleaning steps:

- Drop blank and unnamed columns.
- Normalize source columns to snake_case.
- Convert `starter` values to booleans.
- Convert `game_date` values from Excel serials, dates, or strings.
- Add `game_date_display`.
- Coerce stat columns to numeric.
- Recalculate rates from raw fields instead of trusting workbook formula columns.

## Player Game Output

Output file: `outputs/player_game_summary.csv`

Grain: one row per `game_id + team + player_name`.

Target stats:

- Game context: `season`, `game_id`, `game_date`, `game_date_display`, `matchup`, `team`, `opponent`, `team_score`, `opponent_score`, `result`
- Player identity and role: `player_number`, `player_name`, `starter`, `role_group`
- Box score totals: `minutes`, `pts`, `reb`, `oreb`, `dreb`, `ast`, `tov`, `stl`, `blk`, `fouls`, `fgm`, `fga`, `fg2m`, `fg2a`, `fg3m`, `fg3a`, `ftm`, `fta`
- Calculated shooting and rate metrics: `fg_pct`, `fg2_pct`, `fg3_pct`, `ft_pct`, `efg_pct`, `ts_pct`, `usage_pct`, `ft_rate`, `three_pt_rate`, `two_pt_rate`, `ast_tov_ratio`, `ppsa`
- Per-36 metrics: `pts_per36`, `reb_per36`, `ast_per36`, `stl_per36`, `blk_per36`, `tov_per36`, `fouls_per36`
- Impact metrics: `impact_score_base`, `efficiency_bonus`, `impact_score`

## Team Game Output

Output file: `outputs/team_game_summary.csv`

Grain: one row per `game_id + team`.

Target stats:

- Game context: `season`, `game_id`, `game_date`, `game_date_display`, `team`, `opponent`, `team_score`, `opponent_score`, `result`
- Team box totals: `fgm`, `fga`, `fg2m`, `fg2a`, `fg3m`, `fg3a`, `ftm`, `fta`, `oreb`, `dreb`, `reb`, `ast`, `tov`, `stl`, `blk`, `fouls`, `team_minutes`, `pts`
- Possession context: `poss`, `opp_poss`, `opp_oreb`, `opp_dreb`
- Calculated shooting metrics: `fg_pct`, `fg2_pct`, `fg3_pct`, `ft_pct`, `efg_pct`, `ts_pct`
- Four Factors and style metrics: `tov_pct`, `oreb_pct`, `dreb_pct`, `ft_rate`, `three_pt_rate`, `two_pt_rate`, `assist_rate`
- Rating metrics: `off_rating`, `def_rating`, `net_rating`, `pace`

## Player Season Output

Output file: `outputs/player_season_summary.csv`

Grain: one row per `season + team + player_name`.

Target stats:

- Identity and sample: `season`, `team`, `player_name`, `player_number`, `games_played`, `starts`, `bench_games`, `total_minutes`, `mpg`
- Per-game metrics: `ppg`, `rpg`, `oreb_pg`, `dreb_pg`, `apg`, `spg`, `bpg`, `tov_pg`, `fouls_pg`
- Season totals: `fgm`, `fga`, `fg2m`, `fg2a`, `fg3m`, `fg3a`, `ftm`, `fta`
- Calculated shooting and rate metrics: `fg_pct`, `fg2_pct`, `fg3_pct`, `ft_pct`, `efg_pct`, `ts_pct`, `usage_pct`, `ft_rate`, `three_pt_rate`, `two_pt_rate`, `ast_tov_ratio`, `ppsa`
- Per-36 metrics: `pts_per36`, `reb_per36`, `ast_per36`, `stl_per36`, `blk_per36`, `tov_per36`, `fouls_per36`
- Impact and percentile metrics: `avg_impact_score`, `percentile_scoring`, `percentile_efficiency`, `percentile_playmaking`, `percentile_rebounding`, `percentile_defense`, `percentile_rim_pressure`, `percentile_spacing`, `player_role_label`, `watchability_score`

## Team Season Output

Output file: `outputs/team_season_summary.csv`

Grain: one row per `season + team`.

Target stats:

- Record and scoring: `season`, `team`, `games_played`, `wins`, `losses`, `win_pct`, `pts_for`, `pts_against`, `ppg`, `opp_ppg`, `score_margin_pg`
- Season totals: `fgm`, `fga`, `fg2m`, `fg2a`, `fg3m`, `fg3a`, `ftm`, `fta`, `oreb`, `dreb`, `reb`, `ast`, `tov`, `stl`, `blk`, `fouls`, `poss`
- Calculated shooting metrics: `fg_pct`, `fg2_pct`, `fg3_pct`, `ft_pct`, `efg_pct`, `ts_pct`
- Four Factors and style metrics: `tov_pct`, `oreb_pct`, `dreb_pct`, `ft_rate`, `three_pt_rate`, `two_pt_rate`, `assist_rate`
- Rating metrics: `off_rating`, `def_rating`, `net_rating`, `pace`
- Team ranks: `rank_ppg`, `rank_opp_ppg`, `rank_off_rating`, `rank_def_rating`, `rank_net_rating`, `rank_efg_pct`, `rank_tov_pct`, `rank_oreb_pct`, `rank_ft_rate`

## First-Pass Analysis Outputs

Manual analysis workflow output directory: `analysis/`

Generated files:

- `team_metric_leaders.csv`
- `player_metric_leaders.csv`
- `analysis_summary.md`

These are intended to help decide which visual templates are worth building after reviewing the strongest player and team signals.

Player analysis leaderboards default to `total_minutes >= 40` so tiny samples do not dominate per-minute or watchability leaderboards. The threshold can be changed when manually running the analysis workflow.
