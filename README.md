# WPBA Data Viz Templates Pipeline

Python helper pipeline for WPBA Phase 1 social analytics and data visualization templates.

The pipeline turns the local workbook `data/wpba_stats_2026_clean.xlsx` into clean, analysis-ready helper tables for social graphics, post-game recaps, player highlights, and template mockups.

## What It Builds

- Player game summaries
- Team game summaries
- Player season rollups
- Team season rollups
- Phase 1 visual-template readiness map
- Data dictionary
- QA checks
- Helper Excel workbook with all output tables

## Run The Pipeline

```bash
python3 src/build_wpba_helpers.py --input data/wpba_stats_2026_clean.xlsx --output-dir outputs
```

Generated files land in `outputs/`:

- `player_game_summary.csv`
- `team_game_summary.csv`
- `player_season_summary.csv`
- `team_season_summary.csv`
- `phase1_visual_inputs.csv`
- `data_dictionary.csv`
- `qa_checks.csv`
- `wpba_phase1_helper_outputs.xlsx`

## Verify

```bash
python3 -m unittest discover tests
```

## Source Workbook Contract

Required sheet:

- `team_player_stats_2026`

Optional sheets:

- `team_game_summarys`
- `team_season_summary`

The pipeline recalculates basketball rates from raw fields rather than trusting spreadsheet formula columns. It also normalizes dates, starter flags, numeric stats, source column names, role labels, percentiles, watchability scores, and QA warnings.

## Template Mockups

`wpba_template_mockups/` includes early HTML and PNG references for:

- Player of the Game
- Bench Spark
- Since Last Meeting

