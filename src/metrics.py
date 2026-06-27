"""Basketball metric helpers for the WPBA Phase 1 workbook pipeline."""

from __future__ import annotations

import numpy as np
import pandas as pd


def safe_div(numerator, denominator):
    """Divide safely, returning NaN where the denominator is zero or missing."""
    num = pd.to_numeric(numerator, errors="coerce")
    den = pd.to_numeric(denominator, errors="coerce")
    if not isinstance(num, pd.Series) and not isinstance(den, pd.Series):
        if pd.isna(den) or den == 0:
            return np.nan
        result = num / den
        if np.isinf(result):
            return np.nan
        return float(result)
    result = num / den
    if isinstance(result, pd.Series):
        result = result.where((den != 0) & den.notna(), np.nan)
        return result.replace([np.inf, -np.inf], np.nan)
    if pd.isna(den) or den == 0:
        return np.nan
    if np.isinf(result):
        return np.nan
    return float(result)


def calc_fg_pct(fgm, fga):
    return safe_div(fgm, fga)


def calc_fg2_pct(fg2m, fg2a):
    return safe_div(fg2m, fg2a)


def calc_fg3_pct(fg3m, fg3a):
    return safe_div(fg3m, fg3a)


def calc_ft_pct(ftm, fta):
    return safe_div(ftm, fta)


def calc_efg_pct(fgm, fg3m, fga):
    return safe_div(pd.to_numeric(fgm, errors="coerce") + 0.5 * pd.to_numeric(fg3m, errors="coerce"), fga)


def calc_ts_pct(pts, fga, fta):
    denominator = 2 * (pd.to_numeric(fga, errors="coerce") + 0.44 * pd.to_numeric(fta, errors="coerce"))
    return safe_div(pts, denominator)


def calc_possessions(fga, fta, oreb, tov):
    return (
        pd.to_numeric(fga, errors="coerce")
        + 0.44 * pd.to_numeric(fta, errors="coerce")
        - pd.to_numeric(oreb, errors="coerce")
        + pd.to_numeric(tov, errors="coerce")
    )


def calc_tov_pct(tov, poss):
    return safe_div(tov, poss)


def calc_oreb_pct(oreb, opp_dreb):
    return safe_div(oreb, pd.to_numeric(oreb, errors="coerce") + pd.to_numeric(opp_dreb, errors="coerce"))


def calc_dreb_pct(dreb, opp_oreb):
    return safe_div(dreb, pd.to_numeric(dreb, errors="coerce") + pd.to_numeric(opp_oreb, errors="coerce"))


def calc_ft_rate(fta, fga):
    return safe_div(fta, fga)


def calc_three_pt_rate(fg3a, fga):
    return safe_div(fg3a, fga)


def calc_two_pt_rate(fg2a, fga):
    return safe_div(fg2a, fga)


def calc_assist_rate(ast, fgm):
    return safe_div(ast, fgm)


def calc_off_rating(pts, poss):
    return 100 * safe_div(pts, poss)


def calc_def_rating(opp_pts, opp_poss):
    return 100 * safe_div(opp_pts, opp_poss)


def calc_net_rating(off_rating, def_rating):
    return pd.to_numeric(off_rating, errors="coerce") - pd.to_numeric(def_rating, errors="coerce")


def calc_pace(poss, minutes, game_minutes=40):
    return game_minutes * safe_div(poss, minutes)


def calc_per36(stat, minutes):
    return 36 * safe_div(stat, minutes)


def calc_ast_tov_ratio(ast, tov):
    return safe_div(ast, tov)


def calc_ppsa(pts, fga):
    return safe_div(pts, fga)
