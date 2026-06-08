from typing import Any, Dict, List, Optional, Tuple
import numpy as np


def _match_points(home_goals: int, away_goals: int, is_home: bool) -> float:
  if home_goals == away_goals:
    return 1.0
  home_won = home_goals > away_goals
  if is_home:
    return 3.0 if home_won else 0.0
  return 3.0 if not home_won else 0.0


def _parse_score(match: Dict[str, Any], team_id: int) -> Tuple[Optional[int], Optional[int], bool]:
  score = match.get("score", {}).get("fullTime", {})
  home = score.get("home")
  away = score.get("away")
  if home is None or away is None:
    return None, None, False
  is_home = match.get("homeTeam", {}).get("id") == team_id
  goals_for = home if is_home else away
  goals_against = away if is_home else home
  return goals_for, goals_against, is_home


def compute_form_stats(recent_matches: List[Dict[str, Any]], team_id: int) -> Dict[str, float]:
  points, goals_for, goals_against, wins = [], [], [], 0
  for match in recent_matches:
    gf, ga, is_home = _parse_score(match, team_id)
    if gf is None:
      continue
    home_goals = match["score"]["fullTime"]["home"]
    away_goals = match["score"]["fullTime"]["away"]
    points.append(_match_points(home_goals, away_goals, is_home))
    goals_for.append(gf)
    goals_against.append(ga)
    if gf > ga:
      wins += 1

  n = max(len(points), 1)
  return {
    "form_points_avg": sum(points) / n,
    "goals_for_avg": sum(goals_for) / n if goals_for else 1.2,
    "goals_against_avg": sum(goals_against) / n if goals_against else 1.2,
    "win_rate": wins / n,
    "matches_played": len(points),
  }


def _standing_for_team(standings: List[Dict[str, Any]], team_id: int) -> Dict[str, Any]:
  if not standings:
    return {}
  table = standings[0].get("table", []) if standings else []
  return next((row for row in table if row.get("team", {}).get("id") == team_id), {})


def compute_h2h_stats(
  h2h_matches: List[Dict[str, Any]],
  team1_id: int,
  team2_id: int,
) -> Dict[str, float]:
  home_wins = draws = away_wins = 0
  total_goals_home = total_goals_away = 0
  counted = 0

  for match in h2h_matches:
    score = match.get("score", {}).get("fullTime", {})
    hg, ag = score.get("home"), score.get("away")
    if hg is None or ag is None:
      continue
    counted += 1
    total_goals_home += hg
    total_goals_away += ag
    if match.get("homeTeam", {}).get("id") == team1_id:
      if hg > ag:
        home_wins += 1
      elif hg == ag:
        draws += 1
      else:
        away_wins += 1
    elif match.get("homeTeam", {}).get("id") == team2_id:
      if hg > ag:
        away_wins += 1
      elif hg == ag:
        draws += 1
      else:
        home_wins += 1

  n = max(counted, 1)
  return {
    "h2h_home_win_rate": home_wins / n,
    "h2h_draw_rate": draws / n,
    "h2h_away_win_rate": away_wins / n,
    "h2h_avg_goals_home": total_goals_home / n,
    "h2h_avg_goals_away": total_goals_away / n,
    "h2h_matches": counted,
  }


def _normalize_team_name(name: str) -> str:
  return name.lower().replace("fc ", "").replace(" real", "").strip()


def extract_live_features(
  team1_id: int,
  team2_id: int,
  standings: List[Dict[str, Any]],
  team1_recent: List[Dict[str, Any]],
  team2_recent: List[Dict[str, Any]],
  h2h: Dict[str, Any],
  deep_h2h: Optional[List[Dict[str, Any]]] = None,
  team1_name: str = "",
  team2_name: str = "",
) -> np.ndarray:
  t1_standing = _standing_for_team(standings, team1_id)
  t2_standing = _standing_for_team(standings, team2_id)

  t1_form = compute_form_stats(team1_recent, team1_id)
  t2_form = compute_form_stats(team2_recent, team2_id)
  h2h_stats = compute_h2h_stats(h2h.get("matches", []), team1_id, team2_id)

  t1_pos = float(t1_standing.get("position", 10))
  t2_pos = float(t2_standing.get("position", 10))
  t1_pts = float(t1_standing.get("points", 30))
  t2_pts = float(t2_standing.get("points", 30))
  t1_gd = float(t1_standing.get("goalDifference", 0))
  t2_gd = float(t2_standing.get("goalDifference", 0))

  deep_home_wins = deep_draws = deep_away_wins = 0
  t1_norm = _normalize_team_name(team1_name)
  t2_norm = _normalize_team_name(team2_name)
  if deep_h2h and t1_norm and t2_norm:
    for match in deep_h2h[-10:]:
      try:
        hg = int(match.get("golesLocal", 0))
        ag = int(match.get("golesVisitante", 0))
      except (TypeError, ValueError):
        continue
      local = _normalize_team_name(match.get("EquipoLocal", ""))
      team1_was_home = t1_norm in local or local in t1_norm
      if hg == ag:
        deep_draws += 1
      elif (hg > ag and team1_was_home) or (ag > hg and not team1_was_home):
        deep_home_wins += 1
      else:
        deep_away_wins += 1

  deep_counted = deep_home_wins + deep_draws + deep_away_wins
  deep_n = max(deep_counted, 1)
  deep_home_rate = deep_home_wins / deep_n if deep_counted else 0.33
  deep_draw_rate = deep_draws / deep_n if deep_counted else 0.33
  deep_away_rate = deep_away_wins / deep_n if deep_counted else 0.33

  return np.array([
    1.0,  # home advantage
    t1_pos,
    t2_pos,
    t2_pos - t1_pos,
    t1_pts,
    t2_pts,
    t1_pts - t2_pts,
    t1_gd,
    t2_gd,
    t1_gd - t2_gd,
    t1_form["form_points_avg"],
    t2_form["form_points_avg"],
    t1_form["goals_for_avg"],
    t1_form["goals_against_avg"],
    t2_form["goals_for_avg"],
    t2_form["goals_against_avg"],
    t1_form["win_rate"],
    t2_form["win_rate"],
    h2h_stats["h2h_home_win_rate"],
    h2h_stats["h2h_draw_rate"],
    h2h_stats["h2h_away_win_rate"],
    h2h_stats["h2h_avg_goals_home"],
    h2h_stats["h2h_avg_goals_away"],
    deep_home_rate,
    deep_draw_rate,
    deep_away_rate,
  ], dtype=np.float32)


def build_historical_training_rows(matches: List[Dict[str, str]]) -> Tuple[np.ndarray, np.ndarray]:
  """Build training data from local historical archive using rolling team strength."""
  team_stats: Dict[str, Dict[str, float]] = {}
  features: List[List[float]] = []
  labels: List[int] = []

  def get_stats(team: str) -> Dict[str, float]:
    if team not in team_stats:
      team_stats[team] = {
        "played": 0,
        "wins": 0,
        "draws": 0,
        "goals_for": 0,
        "goals_against": 0,
        "home_played": 0,
        "home_wins": 0,
        "away_played": 0,
        "away_wins": 0,
      }
    return team_stats[team]

  def update_stats(team: str, goals_for: int, goals_against: int, is_home: bool, won: bool, drew: bool):
    stats = get_stats(team)
    stats["played"] += 1
    stats["goals_for"] += goals_for
    stats["goals_against"] += goals_against
    if drew:
      stats["draws"] += 1
    if won:
      stats["wins"] += 1
    if is_home:
      stats["home_played"] += 1
      if won:
        stats["home_wins"] += 1
    else:
      stats["away_played"] += 1
      if won:
        stats["away_wins"] += 1

  sorted_matches = sorted(matches, key=lambda m: (m.get("temporada", ""), m.get("fecha", "")))

  for match in sorted_matches:
    home = match.get("EquipoLocal", "")
    away = match.get("EquipoVisitante", "")
    try:
      hg = int(match.get("golesLocal", 0))
      ag = int(match.get("golesVisitante", 0))
    except ValueError:
      continue

    hs = get_stats(home)
    aws = get_stats(away)
    hp = max(hs["played"], 1)
    ap = max(aws["played"], 1)

    row = [
      1.0,
      hs["wins"] / hp,
      aws["wins"] / ap,
      hs["draws"] / hp,
      aws["draws"] / ap,
      hs["goals_for"] / hp,
      hs["goals_against"] / hp,
      aws["goals_for"] / ap,
      aws["goals_against"] / ap,
      hs["home_wins"] / max(hs["home_played"], 1),
      aws["away_wins"] / max(aws["away_played"], 1),
      (hs["goals_for"] - hs["goals_against"]) / hp,
      (aws["goals_for"] - aws["goals_against"]) / ap,
    ]
    features.append(row)

    if hg > ag:
      labels.append(0)  # home win
    elif hg == ag:
      labels.append(1)  # draw
    else:
      labels.append(2)  # away win

    home_won = hg > ag
    away_won = ag > hg
    drew = hg == ag
    update_stats(home, hg, ag, True, home_won, drew)
    update_stats(away, ag, hg, False, away_won, drew)

  return np.array(features, dtype=np.float32), np.array(labels, dtype=np.int32)
