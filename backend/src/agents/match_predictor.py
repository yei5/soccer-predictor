from typing import Dict, Any, List

from ..models.feature_engineer import compute_form_stats, compute_h2h_stats


class MatchPredictor:
    @staticmethod
    def format_match_context(
        team1: Dict[str, Any], 
        team2: Dict[str, Any], 
        standings: List[Dict[str, Any]], 
        h2h: Dict[str, Any],
        team1_recent: List[Dict[str, Any]],
        team2_recent: List[Dict[str, Any]],
        team1_info: Dict[str, Any] = {},
        team2_info: Dict[str, Any] = {},
        deep_h2h: List[Dict[str, Any]] = [],
        soccer_data_details: Dict[str, Any] = {},
        soccer_data_preview: Dict[str, Any] = {}
    ) -> str:
        # Extract standing info safely
        t1_standing = {}
        t2_standing = {}
        if standings and len(standings) > 0 and 'table' in standings[0]:
            t1_standing = next((s for s in standings[0]['table'] if s['team']['id'] == team1['id']), {})
            t2_standing = next((s for s in standings[0]['table'] if s['team']['id'] == team2['id']), {})
        
        context = f"Match Analysis: {team1['name']} vs {team2['name']}\n"
        context += f"Venue: {team1_info.get('venue', 'Unknown')}\n"
        
        weather = soccer_data_preview.get('match_data', {}).get('weather', {})
        if weather:
            context += f"Weather: {weather.get('temp_c')}°C, {weather.get('description')}\n"
        context += "\n"
        
        context += "--- Team Background ---\n"
        context += f"{team1['name']}: Based in {team1_info.get('address', 'N/A')}, founded in {team1_info.get('founded', 'N/A')}.\n"
        context += f"{team2['name']}: Based in {team2_info.get('address', 'N/A')}, founded in {team2_info.get('founded', 'N/A')}.\n\n"
        
        lineups_root = soccer_data_details.get('lineups', {})
        if lineups_root:
            sidelined = lineups_root.get('sidelined', {})
            t1_injuries = [p.get('player', {}).get('name', 'Unknown') for p in sidelined.get('home', [])]
            t2_injuries = [p.get('player', {}).get('name', 'Unknown') for p in sidelined.get('away', [])]
            context += f"{team1['name']} Injuries/Unavailable: {', '.join(t1_injuries) if t1_injuries else 'None reported'}\n"
            context += f"{team2['name']} Injuries/Unavailable: {', '.join(t2_injuries) if t2_injuries else 'None reported'}\n"
            context += f"Lineup Status: {lineups_root.get('lineup_type', 'projected').capitalize()}\n\n"
        else:
            context += "Lineup and injury data currently unavailable.\n\n"

        context += "--- Current League Standings ---\n"
        if t1_standing or t2_standing:
            context += f"{team1['name']}: Position {t1_standing.get('position', 'N/A')}, Points {t1_standing.get('points', 'N/A')}, GD {t1_standing.get('goalDifference', 'N/A')}\n"
            context += f"{team2['name']}: Position {t2_standing.get('position', 'N/A')}, Points {t2_standing.get('points', 'N/A')}, GD {t2_standing.get('goalDifference', 'N/A')}\n\n"
        else:
            context += "Standings data currently unavailable.\n\n"
        
        context += "--- Recent Form (Last 5 Games) ---\n"
        t1_form = ", ".join([f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']} vs {m['awayTeam']['name'] if m['homeTeam']['id'] == team1['id'] else m['homeTeam']['name']} ({m.get('competition', {}).get('name', 'League')})" for m in team1_recent if m.get('score')])
        t2_form = ", ".join([f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']} vs {m['awayTeam']['name'] if m['homeTeam']['id'] == team2['id'] else m['homeTeam']['name']} ({m.get('competition', {}).get('name', 'League')})" for m in team2_recent if m.get('score')])
        context += f"{team1['name']}: {t1_form if t1_form else 'No recent matches found.'}\n"
        context += f"{team2['name']}: {t2_form if t2_form else 'No recent matches found.'}\n"

        t1_stats = compute_form_stats(team1_recent, team1['id'])
        t2_stats = compute_form_stats(team2_recent, team2['id'])
        context += (
            f"\nForm Metrics — {team1['name']}: "
            f"avg pts/game {t1_stats['form_points_avg']:.2f}, "
            f"GF avg {t1_stats['goals_for_avg']:.2f}, "
            f"GA avg {t1_stats['goals_against_avg']:.2f}, "
            f"win rate {t1_stats['win_rate']:.0%}\n"
        )
        context += (
            f"Form Metrics — {team2['name']}: "
            f"avg pts/game {t2_stats['form_points_avg']:.2f}, "
            f"GF avg {t2_stats['goals_for_avg']:.2f}, "
            f"GA avg {t2_stats['goals_against_avg']:.2f}, "
            f"win rate {t2_stats['win_rate']:.0%}\n\n"
        )
        
        context += "--- Global Head to Head (Live Records) ---\n"
        h2h_matches = h2h.get('matches', [])
        if h2h_matches:
            h2h_stats = compute_h2h_stats(h2h_matches, team1['id'], team2['id'])
            context += (
                f"H2H Summary ({h2h_stats['h2h_matches']} matches): "
                f"{team1['name']} wins {h2h_stats['h2h_home_win_rate']:.0%}, "
                f"draws {h2h_stats['h2h_draw_rate']:.0%}, "
                f"{team2['name']} wins {h2h_stats['h2h_away_win_rate']:.0%}\n"
            )
            for m in h2h_matches:
                score = m.get('score', {}).get('fullTime', {})
                comp = m.get('competition', {}).get('name', 'Unknown Competition')
                context += f"{m.get('utcDate', '')[:10]} [{comp}]: {m['homeTeam']['name']} {score.get('home', '?')}-{score.get('away', '?')} {m['awayTeam']['name']}\n"
        
        sd_prediction = soccer_data_preview.get('match_data', {}).get('prediction', {})
        if sd_prediction:
            context += f"\n--- SoccerData AI Insight ---\n"
            context += f"Projected Outcome: {sd_prediction.get('choice')} (Type: {sd_prediction.get('type')})\n"
            context += f"Excitement Rating: {soccer_data_preview.get('match_data', {}).get('excitement_rating', 'N/A')}/10\n"

        t1_trans = soccer_data_details.get('team1_transfers', {}).get('transfers', {}).get('transfers_in', [])
        t2_trans = soccer_data_details.get('team2_transfers', {}).get('transfers', {}).get('transfers_in', [])
        if t1_trans or t2_trans:
            context += "\n--- Recent Transfers (Key Incomings) ---\n"
            if t1_trans:
                context += f"{team1['name']} IN: " + ", ".join([f"{t.get('player_name')} (from {t.get('from_team', {}).get('name', 'Unknown')})" for t in t1_trans[:3]]) + "\n"
            if t2_trans:
                context += f"{team2['name']} IN: " + ", ".join([f"{t.get('player_name')} (from {t.get('from_team', {}).get('name', 'Unknown')})" for t in t2_trans[:3]]) + "\n"

        if deep_h2h:
            context += "\n--- Deep Historical Archive Records (Local DB) ---\n"
            for m in deep_h2h[-15:]:
                context += f"Season {m['temporada']}: {m['EquipoLocal']} {m['golesLocal']}-{m['golesVisitante']} {m['EquipoVisitante']} (Date: {m['fecha']})\n"
            
        return context
