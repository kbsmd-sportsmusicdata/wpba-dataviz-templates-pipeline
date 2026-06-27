import tempfile
import unittest
from pathlib import Path

import pandas as pd


class WpbaAnalysisTest(unittest.TestCase):
    def test_analysis_outputs_team_and_player_leader_files(self):
        from src.analyze_wpba_outputs import run_analysis

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "outputs"
            analysis_dir = root / "analysis"
            input_dir.mkdir()

            pd.DataFrame([
                {
                    "team": "Alpha",
                    "games_played": 2,
                    "wins": 2,
                    "losses": 0,
                    "ppg": 80.0,
                    "opp_ppg": 70.0,
                    "score_margin_pg": 10.0,
                    "off_rating": 110.0,
                    "def_rating": 95.0,
                    "net_rating": 15.0,
                    "efg_pct": 0.55,
                    "ts_pct": 0.58,
                    "tov_pct": 0.12,
                    "oreb_pct": 0.30,
                    "dreb_pct": 0.72,
                    "ft_rate": 0.24,
                    "three_pt_rate": 0.36,
                    "pace": 78.0,
                },
                {
                    "team": "Beta",
                    "games_played": 2,
                    "wins": 0,
                    "losses": 2,
                    "ppg": 68.0,
                    "opp_ppg": 82.0,
                    "score_margin_pg": -14.0,
                    "off_rating": 92.0,
                    "def_rating": 111.0,
                    "net_rating": -19.0,
                    "efg_pct": 0.44,
                    "ts_pct": 0.47,
                    "tov_pct": 0.18,
                    "oreb_pct": 0.21,
                    "dreb_pct": 0.61,
                    "ft_rate": 0.18,
                    "three_pt_rate": 0.31,
                    "pace": 75.0,
                },
            ]).to_csv(input_dir / "team_season_summary.csv", index=False)

            pd.DataFrame([
                {
                    "team": "Alpha",
                    "player_name": "A Star",
                    "games_played": 2,
                    "total_minutes": 61,
                    "ppg": 22.0,
                    "rpg": 7.0,
                    "apg": 4.5,
                    "ts_pct": 0.62,
                    "usage_pct": 0.31,
                    "pts_per36": 26.0,
                    "reb_per36": 8.0,
                    "ast_per36": 5.2,
                    "stl_per36": 2.0,
                    "blk_per36": 1.0,
                    "avg_impact_score": 31.5,
                    "watchability_score": 91.2,
                    "player_role_label": "Volume Scorer",
                },
                {
                    "team": "Beta",
                    "player_name": "B Guard",
                    "games_played": 2,
                    "total_minutes": 54,
                    "ppg": 15.0,
                    "rpg": 3.0,
                    "apg": 6.0,
                    "ts_pct": 0.51,
                    "usage_pct": 0.24,
                    "pts_per36": 18.0,
                    "reb_per36": 4.0,
                    "ast_per36": 7.1,
                    "stl_per36": 1.2,
                    "blk_per36": 0.1,
                    "avg_impact_score": 20.0,
                    "watchability_score": 76.4,
                    "player_role_label": "Connector",
                },
                {
                    "team": "Beta",
                    "player_name": "Tiny Sample",
                    "games_played": 1,
                    "total_minutes": 2,
                    "ppg": 9.0,
                    "rpg": 1.0,
                    "apg": 0.0,
                    "ts_pct": 1.5,
                    "usage_pct": 0.9,
                    "pts_per36": 162.0,
                    "reb_per36": 18.0,
                    "ast_per36": 0.0,
                    "stl_per36": 0.0,
                    "blk_per36": 0.0,
                    "avg_impact_score": 9.0,
                    "watchability_score": 99.9,
                    "player_role_label": "Small Sample Contributor",
                },
            ]).to_csv(input_dir / "player_season_summary.csv", index=False)

            outputs = run_analysis(input_dir, analysis_dir, top_n=1)

            self.assertEqual({"team_metric_leaders", "player_metric_leaders", "analysis_summary"}, set(outputs))
            self.assertTrue((analysis_dir / "team_metric_leaders.csv").exists())
            self.assertTrue((analysis_dir / "player_metric_leaders.csv").exists())
            self.assertTrue((analysis_dir / "analysis_summary.md").exists())

            team_leaders = pd.read_csv(analysis_dir / "team_metric_leaders.csv")
            player_leaders = pd.read_csv(analysis_dir / "player_metric_leaders.csv")
            summary = (analysis_dir / "analysis_summary.md").read_text()

            self.assertIn("net_rating", set(team_leaders["metric"]))
            self.assertEqual(team_leaders.loc[team_leaders["metric"] == "net_rating", "leader"].iloc[0], "Alpha")
            self.assertIn("watchability_score", set(player_leaders["metric"]))
            self.assertEqual(player_leaders.loc[player_leaders["metric"] == "watchability_score", "leader"].iloc[0], "A Star")
            self.assertNotIn("Tiny Sample", set(player_leaders["leader"]))
            self.assertIn("WPBA Processed Dataset Analysis", summary)


if __name__ == "__main__":
    unittest.main()
