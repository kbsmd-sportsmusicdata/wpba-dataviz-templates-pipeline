# Codex Handoff: WPBA Phase 1 Social Analytics Data Pipeline

## Project Goal

Build a Python-based data transformation and advanced metric pipeline for the workbook:

`week1_week2_wpba_stats.xlsx`

The pipeline should clean the current WPBA Week 1–2 player/game data, generate helper summary tables, calculate advanced basketball metrics, and export analysis-ready CSV files that can power fan-facing social media data visual templates.

This replaces the original Google Sheets / Apps Script workflow. The preferred implementation is now Python-first, repeatable, and suitable for future automation.

---

## Current Workbook Structure

The uploaded workbook currently contains three tabs:

1. `team_player_stats_2026`
2. `team_game_summarys`
3. `team_season_summary`

### Primary Source Tab

Use `team_player_stats_2026` as the main source table.

Current columns observed in `team_player_stats_2026`:

```text
source_sheet
game_id
game_date
matchup
team
opponent
team_score
opponent_score
player_number
player_name
starter
minutes
time_mmss
mpg_minutes
mpg_mmss
pts
fg2m
fg2a
fg3m
fg3a
ftm
fta
fgm
fga
fg2_pct
fg3_pct
ft_pct
efg_pct
ts_pct
two_pt_fouled
two_pt_rate
three_pt_rate
ast
fouls
tov
reb
oreb
dreb
reb_pct
blk
stl
usage_pct_source
usage_pct_calc
off_ppp
def_ppp
off_poss
team_minutes_sum
team_fga
team_fta
team_tov
pts_per36
reb_per36
ast_per36
tov_per36
stl_per36
blk_per36
fouls_per36
shot_pair_recovery_flags
[blank column]
team_ts_pct
player_relative_ts_pct
tov_rate
ft_rate
ppsa
pct_pts_2pt
pct_pts_3pt
pct_pts_ft
ast_tov_ratio
```

### Existing Supporting Tabs

`team_game_summarys` currently appears to include game schedule/final score information. It includes completed games and upcoming games.

Observed columns:

```text
game_time
game_id
game_date
team
opponent
team_score
opponent_score
result
```

`team_season_summary` currently includes basic standings.

Observed columns:

```text
Season
Team
games_played
Wins
Losses
Win_pct
Pts_For
Pts_Against
Games_Behind
L10
Streak
Streak_Wins_or_Losses
```

Important: Do not depend on these supporting tabs as the sole source of truth for metrics. Rebuild clean calculated summaries from `team_player_stats_2026`, and optionally use `team_game_summarys` for game time / upcoming schedule context and `team_season_summary` for current standings context.

---

## Desired Output Files

Create an `outputs/` folder and export the following CSVs:

1. `outputs/player_game_summary.csv`
2. `outputs/team_game_summary.csv`
3. `outputs/player_season_summary.csv`
4. `outputs/team_season_summary.csv`
5. `outputs/phase1_visual_inputs.csv`
6. `outputs/data_dictionary.csv`
7. Optional: `outputs/qa_checks.csv`

Also create a cleaned Excel workbook if convenient:

`outputs/wpba_phase1_helper_outputs.xlsx`

with one sheet for each output table.

---

## Recommended Repo / File Structure

```text
wpba-social-analytics-pipeline/
├── data/
│   └── week1_week2_wpba_stats.xlsx
├── outputs/
│   ├── player_game_summary.csv
│   ├── team_game_summary.csv
│   ├── player_season_summary.csv
│   ├── team_season_summary.csv
│   ├── phase1_visual_inputs.csv
│   ├── data_dictionary.csv
│   └── qa_checks.csv
├── src/
│   ├── build_wpba_helpers.py
│   ├── metrics.py
│   ├── role_labels.py
│   └── visual_inputs.py
├── README.md
└── requirements.txt
```

Minimum `requirements.txt`:

```text
pandas
numpy
openpyxl
```

---

## Implementation Requirements

### 1. Main CLI Script

Create:

`src/build_wpba_helpers.py`

It should be runnable as:

```bash
python src/build_wpba_helpers.py --input data/week1_week2_wpba_stats.xlsx --output-dir outputs
```

Expected behavior:

1. Load workbook.
2. Read `team_player_stats_2026`.
3. Clean column names.
4. Normalize dates, booleans, numeric columns.
5. Build all summary tables.
6. Export CSVs.
7. Export optional Excel workbook.
8. Print a concise QA summary to terminal.

---

## Cleaning Requirements

### Column Names

Normalize all columns to snake_case. Preserve known names where possible.

Remove blank/unnamed columns.

Examples:

```python
"Season" -> "season"
"Team" -> "team"
"Win_pct" -> "win_pct"
"Unnamed: 58" -> drop
```

### Dates

`game_date` may be stored as Excel serial dates. Convert to real dates.

Expected examples:
- Excel serial `46186` should convert to a June 2026 date.
- If existing values appear as strings like `6/13`, parse them where possible.
- Preserve a display column if useful: `game_date_display`.

### Starter

Normalize `starter` into boolean:

```text
true / TRUE / Yes / 1 -> True
false / FALSE / No / 0 / blank -> False
```

### Numeric Columns

Coerce all stat columns to numeric. Invalid values should become `NaN`, not strings.

Use safe division helpers so divide-by-zero returns `NaN`.

---

## Metric Helper Functions

Create `src/metrics.py`.

Required functions:

```python
safe_div(numerator, denominator)
calc_fg_pct(fgm, fga)
calc_fg2_pct(fg2m, fg2a)
calc_fg3_pct(fg3m, fg3a)
calc_ft_pct(ftm, fta)
calc_efg_pct(fgm, fg3m, fga)
calc_ts_pct(pts, fga, fta)
calc_possessions(fga, fta, oreb, tov)
calc_tov_pct(tov, poss)
calc_oreb_pct(oreb, opp_dreb)
calc_dreb_pct(dreb, opp_oreb)
calc_ft_rate(fta, fga)
calc_three_pt_rate(fg3a, fga)
calc_two_pt_rate(fg2a, fga)
calc_assist_rate(ast, fgm)
calc_off_rating(pts, poss)
calc_def_rating(opp_pts, opp_poss)
calc_net_rating(off_rating, def_rating)
calc_pace(poss, minutes, game_minutes=40)
calc_per36(stat, minutes)
calc_ast_tov_ratio(ast, tov)
calc_ppsa(pts, fga)
```

Use these formulas:

```text
FG% = FGM / FGA
2P% = FG2M / FG2A
3P% = FG3M / FG3A
FT% = FTM / FTA
eFG% = (FGM + 0.5 * 3PM) / FGA
TS% = PTS / [2 * (FGA + 0.44 * FTA)]
Possessions = FGA + 0.44 * FTA - OREB + TOV
TOV% = TOV / Possessions
OREB% = OREB / (OREB + Opponent DREB)
DREB% = DREB / (DREB + Opponent OREB)
FT Rate = FTA / FGA
3P Attempt Rate = 3PA / FGA
2P Attempt Rate = 2PA / FGA
Assist Rate = AST / FGM
Offensive Rating = 100 * PTS / Possessions
Defensive Rating = 100 * Opponent PTS / Opponent Possessions
Net Rating = Offensive Rating - Defensive Rating
Pace = 40 * Possessions / Team Minutes
Per 36 = Stat / Minutes * 36
AST/TO = AST / TOV
PPSA = PTS / FGA
```

---

## Output Table 1: `player_game_summary.csv`

One row per player per game.

Source: `team_player_stats_2026`

Required columns:

```text
season
game_id
game_date
game_date_display
matchup
team
opponent
team_score
opponent_score
result
player_number
player_name
starter
role_group
minutes
pts
reb
oreb
dreb
ast
tov
stl
blk
fouls
fgm
fga
fg2m
fg2a
fg3m
fg3a
ftm
fta
fg_pct
fg2_pct
fg3_pct
ft_pct
efg_pct
ts_pct
usage_pct
ft_rate
three_pt_rate
two_pt_rate
ast_tov_ratio
ppsa
pts_per36
reb_per36
ast_per36
stl_per36
blk_per36
tov_per36
fouls_per36
impact_score_base
efficiency_bonus
impact_score
```

Rules:

- `season` should be `2026`.
- `result = W` when `team_score > opponent_score`, `L` when `team_score < opponent_score`, else blank.
- `role_group = Starter` if starter is True, else `Bench`.
- `usage_pct` should use `usage_pct_calc` when available; otherwise fallback to `usage_pct_source`.
- Recalculate all core percentages and rates from raw fields rather than trusting existing calculated columns.
- Preserve existing calculated columns only as fallback when raw fields are unavailable.

Impact score:

```text
impact_score_base =
PTS
+ 1.2 * REB
+ 1.5 * AST
+ 3.0 * STL
+ 3.0 * BLK
- 1.5 * TOV
```

Efficiency bonus:

```text
efficiency_bonus = 10 * (player_ts_pct - team_ts_pct)
```

If team TS% lookup is unavailable, set efficiency bonus to `0`.

Final:

```text
impact_score = impact_score_base + efficiency_bonus
```

---

## Output Table 2: `team_game_summary.csv`

One row per team per game.

Source: aggregate from `player_game_summary`.

Required columns:

```text
season
game_id
game_date
game_date_display
team
opponent
team_score
opponent_score
result
fgm
fga
fg2m
fg2a
fg3m
fg3a
ftm
fta
oreb
dreb
reb
ast
tov
stl
blk
fouls
team_minutes
poss
opp_poss
fg_pct
fg2_pct
fg3_pct
ft_pct
efg_pct
ts_pct
tov_pct
oreb_pct
dreb_pct
ft_rate
three_pt_rate
two_pt_rate
assist_rate
off_rating
def_rating
net_rating
pace
```

Aggregation rules:

- Group by `season`, `game_id`, `team`.
- Sum raw player stats.
- Use first non-null for game metadata and scores.
- Join each team row to the opponent row from the same `game_id` to retrieve:
  - `opp_poss`
  - opponent offensive rebounds
  - opponent defensive rebounds
  - opponent points

Caution:
Some games may only have one team row if source data is incomplete. In that case, allow opponent-dependent stats to be blank and record this in QA.

---

## Output Table 3: `team_season_summary.csv`

One row per team.

Source: aggregate from `team_game_summary`.

Required columns:

```text
season
team
games_played
wins
losses
win_pct
pts_for
pts_against
ppg
opp_ppg
score_margin_pg
fgm
fga
fg2m
fg2a
fg3m
fg3a
ftm
fta
oreb
dreb
reb
ast
tov
stl
blk
fouls
poss
fg_pct
fg2_pct
fg3_pct
ft_pct
efg_pct
ts_pct
tov_pct
oreb_pct
dreb_pct
ft_rate
three_pt_rate
two_pt_rate
assist_rate
off_rating
def_rating
net_rating
pace
rank_ppg
rank_opp_ppg
rank_off_rating
rank_def_rating
rank_net_rating
rank_efg_pct
rank_tov_pct
rank_oreb_pct
rank_ft_rate
```

Aggregation rules:

- Include only completed games with non-null scores.
- Recalculate all percentages from season totals.
- Ratings should be based on total points and total possessions, not averages of game-level ratings.
- `pace` can be the weighted average or calculated from total possessions / total minutes.

Ranking rules:

Higher is better:
- `ppg`
- `off_rating`
- `net_rating`
- `efg_pct`
- `oreb_pct`
- `ft_rate`

Lower is better:
- `opp_ppg`
- `def_rating`
- `tov_pct`

---

## Output Table 4: `player_season_summary.csv`

One row per player/team.

Source: aggregate from `player_game_summary`.

Required columns:

```text
season
team
player_name
player_number
games_played
starts
bench_games
total_minutes
mpg
ppg
rpg
oreb_pg
dreb_pg
apg
spg
bpg
tov_pg
fouls_pg
fgm
fga
fg2m
fg2a
fg3m
fg3a
ftm
fta
fg_pct
fg2_pct
fg3_pct
ft_pct
efg_pct
ts_pct
usage_pct
ft_rate
three_pt_rate
two_pt_rate
ast_tov_ratio
ppsa
pts_per36
reb_per36
ast_per36
stl_per36
blk_per36
tov_per36
fouls_per36
avg_impact_score
percentile_scoring
percentile_efficiency
percentile_playmaking
percentile_rebounding
percentile_defense
percentile_rim_pressure
percentile_spacing
player_role_label
watchability_score
```

Aggregation rules:

- Sum raw stats and recalculate rates from totals.
- `usage_pct` should be minutes-weighted average.
- Per-game stats divide by games played.
- Per-36 stats use total stats / total minutes * 36.
- Percentiles are league-wide percentiles for now because the workbook does not currently have a reliable player position column.
- If a position column is added later, support position-adjusted percentiles as a future enhancement.

---

## Percentile Logic

Create overall league-wide percentile columns using all players in `player_season_summary`.

Suggested definitions:

```text
percentile_scoring = percentile rank of pts_per36
percentile_efficiency = percentile rank of ts_pct
percentile_playmaking = percentile rank of ast_per36 or ast_tov_ratio
percentile_rebounding = percentile rank of reb_per36
percentile_defense = percentile rank of combined stl_per36 + blk_per36
percentile_rim_pressure = percentile rank of ft_rate + two_pt_rate
percentile_spacing = percentile rank of three_pt_rate + fg3_pct
```

Composite columns may be calculated first:

```text
defense_activity_score = stl_per36 + blk_per36
rim_pressure_score = average percentile of ft_rate and two_pt_rate
spacing_score = average percentile of three_pt_rate and fg3_pct
```

All percentiles should be scaled 0–100.

---

## Role Labels

Create `src/role_labels.py`.

Use simple, explainable rules for fan-facing social cards.

Suggested labels:

```text
Volume Scorer
Efficiency Finisher
Rim Pressure Creator
Floor Spacer
Connector
Defensive Disruptor
Glass Cleaner
Balanced Contributor
```

Rule suggestions:

- `Volume Scorer`: high scoring percentile and high usage
- `Efficiency Finisher`: high efficiency percentile and high PPSA
- `Rim Pressure Creator`: high rim pressure percentile
- `Floor Spacer`: high spacing percentile
- `Connector`: high playmaking percentile and good AST/TO
- `Defensive Disruptor`: high defensive percentile
- `Glass Cleaner`: high rebounding percentile
- `Balanced Contributor`: fallback label

Pick the strongest label based on the player’s highest percentile category, but avoid assigning misleading labels when the player has very low minutes. For low-minute players, use `Small Sample Contributor` if total minutes is below a reasonable threshold.

Suggested small-sample threshold:
- `total_minutes < 40` for current two-week dataset

---

## Watchability Score

Create a 0–100 `watchability_score`.

Suggested weighted formula:

```text
watchability_score =
0.25 * percentile_scoring
+ 0.20 * percentile_efficiency
+ 0.20 * max(percentile_rebounding, percentile_spacing, percentile_rim_pressure)
+ 0.20 * max(percentile_playmaking, percentile_defense)
+ 0.15 * percentile_rank(avg_impact_score)
```

Round to 1 decimal.

---

## Output Table 5: `phase1_visual_inputs.csv`

This table maps the helper outputs to the first set of social templates.

Rows:

1. `Matchup Overview`
2. `Four Factors Tug-of-War`
3. `Since Last Meeting`
4. `Why You Should Watch`
5. `Final Score`
6. `How They Won`
7. `Player of the Game`
8. `Team Edge Recap`

Required columns:

```text
visual_name
use_case
primary_source_table
secondary_source_table
required_fields
available_now
missing_fields
build_readiness
recommended_chart_type
notes
```

Use this mapping:

### Matchup Overview

Source:
- `team_season_summary`
- optionally `team_game_summarys` for upcoming schedule rows

Fields:
- team, opponent, record, ppg, opp_ppg, off_rating, def_rating, net_rating, pace, ranks

Chart type:
- KPI cards + team comparison bars

### Four Factors Tug-of-War

Source:
- `team_season_summary`

Fields:
- efg_pct, tov_pct, oreb_pct, ft_rate

Chart type:
- diverging bars

### Since Last Meeting

Source:
- `team_game_summary`
- `team_season_summary`

Fields:
- prior head-to-head games, current form, ppg, efg_pct, tov_pct, oreb_pct, ft_rate, net_rating

Chart type:
- delta cards or slopegraph

Fallback if no prior matchup:
- Use “Since Opening Weekend” or “Last 4 Games Trend.”

### Why You Should Watch

Source:
- `player_season_summary`

Fields:
- player_name, team, ppg, rpg, apg, ts_pct, usage_pct, percentiles, role label, watchability_score

Chart type:
- player card + percentile bars

### Final Score

Source:
- `team_game_summary`

Fields:
- team, opponent, team_score, opponent_score, result, top performers

Chart type:
- score card + top performers

### How They Won

Source:
- `team_game_summary`

Fields:
- four factor edges, rebound edge, assist edge, defensive event edge

Chart type:
- evidence tiles / edge cards

### Player of the Game

Source:
- `player_game_summary`

Fields:
- impact_score, pts, reb, ast, stl, blk, ts_pct, usage_pct

Chart type:
- player stat card + impact badge

### Team Edge Recap

Source:
- `team_game_summary`

Fields:
- stat edges across shooting, glass, turnovers, assists, steals, blocks, FT rate

Chart type:
- stat edge grid

---

## Output Table 6: `data_dictionary.csv`

Include columns:

```text
table_name
field_name
field_type
definition
formula
source_table
notes
```

Document:
- all output tables
- all advanced metrics
- all composite scores
- all known limitations

Known limitations to include:

```text
No play-by-play yet.
No shot location or shot zone data yet.
No quarter scores unless another source is added.
No player position column yet.
No player photo URLs yet.
No lineup/on-off data yet.
Clutch and turning point templates require play-by-play later.
Pressure Points and Shot Diet templates require shot zone/location data later.
Percentiles are currently league-wide, not position-adjusted.
Two weeks of data means small-sample volatility is high.
```

---

## QA Checks

Create `outputs/qa_checks.csv` with at least these checks:

```text
check_name
status
details
```

Required checks:

1. Source rows loaded.
2. Blank/unnamed columns removed.
3. Numeric coercion completed.
4. No duplicate player-game rows based on `game_id + team + player_name`.
5. Team-game row count equals number of unique `game_id + team` combinations.
6. Team score in `team_game_summary` matches `team_score` from player rows.
7. Team points sum equals `team_score` when full box score data is present.
8. Possessions are non-negative.
9. No formula-derived fields contain infinite values.
10. Percentiles are between 0 and 100.
11. Completed games only included in season summaries.
12. Missing opponent row count documented.

Do not fail hard for small discrepancies. Flag them clearly.

---

## README Requirements

Create a short `README.md` explaining:

1. What the pipeline does.
2. How to run it.
3. Input workbook expectations.
4. Output files.
5. Metric definitions.
6. Limitations.
7. How the outputs map to social media visual templates.

Suggested project description:

```text
This pipeline transforms WPBA Week 1–2 player game logs into clean helper tables for fan-facing social media analytics templates. It calculates team and player summaries, Four Factors, efficiency metrics, role labels, player percentiles, impact scores, and visual-ready inputs for Phase 1 pre-game and post-game carousel graphics.
```

---

## Phase 1 Visual Template Scope

The output tables should support these eight initial visual templates:

### Pre-game / preview-oriented

1. Matchup Overview
2. Four Factors Tug-of-War
3. Since Last Meeting
4. Why You Should Watch

### Post-game / recap-oriented

5. Final Score
6. How They Won
7. Player of the Game
8. Team Edge Recap

Future templates that should be explicitly noted as requiring additional data:

1. Pressure Points: needs shot zone/location data
2. Bench Impact: needs reliable starter/bench and preferably lineup/on-off data
3. Clutch Watch: needs play-by-play
4. Turning Point: needs play-by-play
5. Clutch Closeout: needs play-by-play
6. What It Means Next: needs standings history / next schedule context

Note: A basic version of Bench Impact can be created from the `starter` flag, but premium bench impact requires lineup data and plus-minus/on-off context.

---

## Design / Product Context

These outputs will eventually feed 1:1 Instagram/Threads carousel graphics for a developmental women’s basketball league.

The visual system should support:
- public-facing storytelling
- quick pre-game matchup previews
- post-game recap graphics
- player role/archetype cards
- comparison graphics
- repeatable content generation
- future automation from updated data

The data pipeline should prioritize clean, reliable, repeatable outputs over one-off spreadsheet formulas.

Tone of the visual outputs:
- fan-friendly
- analytically credible
- mobile-first
- focused on “why should I watch?” and “how did they win?”

---

## Acceptance Criteria

The task is complete when:

1. Running the CLI script generates all expected CSVs.
2. The optional Excel workbook exports successfully.
3. `team_game_summary.csv` has one row per team per game.
4. `team_season_summary.csv` has one row per team.
5. `player_game_summary.csv` has one row per player per game.
6. `player_season_summary.csv` has one row per player/team.
7. Percentile columns are present and scaled 0–100.
8. Role labels are populated.
9. Watchability scores are populated.
10. QA checks are exported.
11. README explains the workflow clearly.
12. No infinite values or obvious divide-by-zero errors appear in outputs.

---

## Suggested First Implementation Order

1. Create `metrics.py`.
2. Create `build_wpba_helpers.py`.
3. Load and clean `team_player_stats_2026`.
4. Build `player_game_summary`.
5. Build `team_game_summary`.
6. Build `team_season_summary`.
7. Build `player_season_summary`.
8. Add percentiles, role labels, and watchability scores.
9. Build `phase1_visual_inputs`.
10. Build `data_dictionary`.
11. Add QA checks.
12. Export all outputs.
13. Write README.

---

## Notes for Codex

Be pragmatic. The first version does not need to be perfect, but it should be clean and repeatable.

Prioritize:
- clean source loading
- safe calculations
- transparent formulas
- easy CSV exports
- useful QA output
- clear names that can be used directly in future visualization scripts

Avoid:
- hardcoded row numbers
- spreadsheet formula dependencies
- manual edits
- silent failures
- overwriting source files

