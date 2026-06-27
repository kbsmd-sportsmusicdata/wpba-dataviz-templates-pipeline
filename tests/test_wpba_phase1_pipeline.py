import math
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class WpbaMetricHelpersTest(unittest.TestCase):
    def test_metric_helpers_return_nan_for_zero_denominators(self):
        from src import metrics

        self.assertTrue(math.isnan(metrics.safe_div(3, 0)))
        self.assertTrue(math.isnan(metrics.calc_fg_pct(1, 0)))
        self.assertTrue(math.isnan(metrics.calc_ts_pct(10, 0, 0)))
        self.assertEqual(metrics.calc_per36(18, 36), 18)

    def test_metric_helpers_match_handoff_formulas(self):
        from src import metrics

        self.assertAlmostEqual(metrics.calc_efg_pct(8, 2, 16), 0.5625)
        self.assertAlmostEqual(metrics.calc_ts_pct(20, 16, 4), 20 / (2 * (16 + 0.44 * 4)))
        self.assertAlmostEqual(metrics.calc_possessions(16, 4, 3, 5), 16 + 0.44 * 4 - 3 + 5)
        self.assertAlmostEqual(metrics.calc_off_rating(80, 72), 100 * 80 / 72)
        self.assertAlmostEqual(metrics.calc_net_rating(111.1, 100.0), 11.1)
        self.assertAlmostEqual(metrics.calc_pace(72, 200), 40 * 72 / 200)
        self.assertAlmostEqual(metrics.calc_ppsa(20, 16), 1.25)


def build_fixture_workbook(path: Path) -> None:
    rows = [
        {
            "source_sheet": "fixture",
            "game_id": "g1",
            "game_date": 46186,
            "matchup": "Alpha vs Beta",
            "team": "Alpha",
            "opponent": "Beta",
            "team_score": 60,
            "opponent_score": 55,
            "player_number": 1,
            "player_name": "A Starter",
            "starter": "Yes",
            "minutes": 30,
            "pts": 20,
            "fg2m": 5,
            "fg2a": 8,
            "fg3m": 2,
            "fg3a": 5,
            "ftm": 4,
            "fta": 4,
            "fgm": 7,
            "fga": 13,
            "ast": 4,
            "fouls": 2,
            "tov": 2,
            "reb": 6,
            "oreb": 2,
            "dreb": 4,
            "blk": 1,
            "stl": 2,
            "usage_pct_source": 0.2,
            "usage_pct_calc": 0.25,
            "team_ts_pct": "formula text",
            "Unnamed: 58": None,
        },
        {
            "source_sheet": "fixture",
            "game_id": "g1",
            "game_date": 46186,
            "matchup": "Alpha vs Beta",
            "team": "Alpha",
            "opponent": "Beta",
            "team_score": 60,
            "opponent_score": 55,
            "player_number": 2,
            "player_name": "A Bench",
            "starter": "No",
            "minutes": 10,
            "pts": 40,
            "fg2m": 10,
            "fg2a": 15,
            "fg3m": 5,
            "fg3a": 10,
            "ftm": 5,
            "fta": 6,
            "fgm": 15,
            "fga": 25,
            "ast": 2,
            "fouls": 1,
            "tov": 1,
            "reb": 5,
            "oreb": 1,
            "dreb": 4,
            "blk": 0,
            "stl": 1,
            "usage_pct_source": 0.3,
            "usage_pct_calc": np.nan,
            "team_ts_pct": "formula text",
            "Unnamed: 58": None,
        },
        {
            "source_sheet": "fixture",
            "game_id": "g1",
            "game_date": 46186,
            "matchup": "Alpha vs Beta",
            "team": "Beta",
            "opponent": "Alpha",
            "team_score": 55,
            "opponent_score": 60,
            "player_number": 3,
            "player_name": "B Starter",
            "starter": True,
            "minutes": 40,
            "pts": 55,
            "fg2m": 14,
            "fg2a": 25,
            "fg3m": 5,
            "fg3a": 12,
            "ftm": 12,
            "fta": 16,
            "fgm": 19,
            "fga": 37,
            "ast": 7,
            "fouls": 3,
            "tov": 8,
            "reb": 16,
            "oreb": 5,
            "dreb": 11,
            "blk": 3,
            "stl": 2,
            "usage_pct_source": 0.36,
            "usage_pct_calc": 0.34,
            "team_ts_pct": "formula text",
            "Unnamed: 58": None,
        },
        {
            "source_sheet": "fixture",
            "game_id": "g2",
            "game_date": "6/14/2026",
            "matchup": "Alpha vs Gamma",
            "team": "Alpha",
            "opponent": "Gamma",
            "team_score": 50,
            "opponent_score": 0,
            "player_number": 1,
            "player_name": "A Starter",
            "starter": "1",
            "minutes": 20,
            "pts": 50,
            "fg2m": 12,
            "fg2a": 20,
            "fg3m": 6,
            "fg3a": 12,
            "ftm": 8,
            "fta": 10,
            "fgm": 18,
            "fga": 32,
            "ast": 5,
            "fouls": 2,
            "tov": 3,
            "reb": 8,
            "oreb": 3,
            "dreb": 5,
            "blk": 2,
            "stl": 1,
            "usage_pct_source": 0.4,
            "usage_pct_calc": 0.42,
            "team_ts_pct": "formula text",
            "Unnamed: 58": None,
        },
    ]
    games = pd.DataFrame([
        {
            "game_time": "12:00:00",
            "game_id": "g1",
            "game_date": "2026-06-13",
            "team": "Alpha",
            "opponent": "Beta",
            "team_score": 60,
            "opponent_score": 55,
            "result": "",
        },
        {
            "game_time": "14:00:00",
            "game_id": "g2",
            "game_date": "2026-06-14",
            "team": "Alpha",
            "opponent": "Gamma",
            "team_score": 50,
            "opponent_score": 0,
            "result": "",
        },
    ])
    standings = pd.DataFrame([
        {"Season": 2026, "Team": "Alpha", "games_played": 2, "Wins": 2, "Losses": 0},
        {"Season": 2026, "Team": "Beta", "games_played": 1, "Wins": 0, "Losses": 1},
    ])
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(rows).to_excel(writer, sheet_name="team_player_stats_2026", index=False)
        games.to_excel(writer, sheet_name="team_game_summarys", index=False)
        standings.to_excel(writer, sheet_name="team_season_summary", index=False)


class WpbaPipelineTest(unittest.TestCase):
    def test_pipeline_cleans_workbook_and_exports_expected_outputs(self):
        from src.build_wpba_helpers import run_pipeline

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workbook = tmp_path / "fixture.xlsx"
            output_dir = tmp_path / "outputs"
            build_fixture_workbook(workbook)

            outputs = run_pipeline(workbook, output_dir)

            expected_files = {
                "player_game_summary.csv",
                "team_game_summary.csv",
                "player_season_summary.csv",
                "team_season_summary.csv",
                "phase1_visual_inputs.csv",
                "data_dictionary.csv",
                "qa_checks.csv",
                "wpba_phase1_helper_outputs.xlsx",
            }
            self.assertTrue(expected_files.issubset({p.name for p in output_dir.iterdir()}))
            self.assertIn("player_game_summary", outputs)
            self.assertEqual(len(outputs["source_clean"]), 4)
            self.assertNotIn("unnamed_58", outputs["source_clean"].columns)
            self.assertTrue(outputs["player_game_summary"]["starter"].isin([True, False]).all())

    def test_pipeline_outputs_grain_metrics_labels_and_qa(self):
        from src.build_wpba_helpers import run_pipeline

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workbook = tmp_path / "fixture.xlsx"
            output_dir = tmp_path / "outputs"
            build_fixture_workbook(workbook)

            outputs = run_pipeline(workbook, output_dir)

            player_game = outputs["player_game_summary"]
            team_game = outputs["team_game_summary"]
            player_season = outputs["player_season_summary"]
            team_season = outputs["team_season_summary"]
            qa = outputs["qa_checks"]

            self.assertEqual(player_game.duplicated(["game_id", "team", "player_name"]).sum(), 0)
            self.assertEqual(team_game.duplicated(["game_id", "team"]).sum(), 0)
            self.assertEqual(team_game.shape[0], 3)
            self.assertEqual(player_season.duplicated(["season", "team", "player_name"]).sum(), 0)
            self.assertEqual(team_season.duplicated(["season", "team"]).sum(), 0)
            self.assertTrue(player_season["watchability_score"].between(0, 100).all())
            self.assertTrue(player_season["percentile_scoring"].between(0, 100).all())
            self.assertIn("Small Sample Contributor", set(player_season["player_role_label"]))
            self.assertIn("missing_opponent_row_count", set(qa["check_name"]))
            self.assertFalse(np.isinf(player_game.select_dtypes(include=[np.number]).to_numpy()).any())
            self.assertFalse(np.isinf(team_game.select_dtypes(include=[np.number]).to_numpy()).any())
            alpha_g1 = team_game[(team_game["game_id"] == "g1") & (team_game["team"] == "Alpha")].iloc[0]
            self.assertEqual(alpha_g1["result"], "W")
            self.assertGreater(alpha_g1["off_rating"], 0)


if __name__ == "__main__":
    unittest.main()
