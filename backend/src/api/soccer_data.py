import os
import json
import requests
import time
from typing import Optional, Dict, Any, List
from ..config.settings import settings

class SoccerDataClient:
    BASE_URL = "https://api.soccerdataapi.com"
    MOCK_DATA_DIR = "backend/data/SoccerDataAPIex"
    
    def __init__(self, api_key: Optional[str] = None, use_mock: bool = False):
        self.api_key = (api_key or settings.SOCCER_DATA_API_KEY).strip()
        self.use_mock = use_mock
        self.headers = {"Accept-Encoding": "gzip"}

    def _get_mock_data(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(self.MOCK_DATA_DIR, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.use_mock:
            # Route to local files based on endpoint
            mapping = {
                "country": "get-country.json",
                "league": "get-league.json",
                "livescores": "get-livescores.json",
                "match": "get-match.json",
                "match-preview": "get-match-preview.json",
                "transfers": "get-transfers.json",
                "head-to-head": "get-head-to-head.json"
            }
            # Simple match for match/123 etc
            base_key = endpoint.split('/')[0]
            return self._get_mock_data(mapping.get(base_key, ""))

        url = f"{self.BASE_URL}/{endpoint}/"
        if params is None:
            params = {}
        params["auth_token"] = self.api_key
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"SoccerData API Rate limit exceeded. Waiting for {retry_after} seconds...")
            time.sleep(retry_after)
            return self._make_request(endpoint, params)
            
        response.raise_for_status()
        return response.json()

    def get_countries(self) -> List[Dict[str, Any]]:
        data = self._make_request("country")
        return data.get("results", [])

    def get_leagues(self, country_id: Optional[int] = None) -> List[Dict[str, Any]]:
        params = {"country_id": country_id} if country_id else {}
        data = self._make_request("league", params=params)
        return data.get("results", [])

    def get_upcoming_matches(self) -> List[Dict[str, Any]]:
        data = self._make_request("livescores")
        return data.get("results", [])

    def get_match_details(self, match_id: int) -> Dict[str, Any]:
        """Fetch detailed info for a specific match (lineups, injuries)."""
        return self._make_request(f"match/{match_id}")

    def get_match_preview(self, match_id: int) -> Dict[str, Any]:
        """Fetch AI-powered match preview (predictions, weather)."""
        return self._make_request(f"match-preview/{match_id}")

    def get_transfers(self, team_id: int) -> Dict[str, Any]:
        """Fetch recent transfers for a team."""
        params = {"team_id": team_id}
        return self._make_request("transfers", params=params)

    def get_h2h_stats(self, team1_id: int, team2_id: int) -> Dict[str, Any]:
        params = {"team_1_id": team1_id, "team_2_id": team2_id}
        return self._make_request("head-to-head", params=params)

    def find_team_id(self, team_name: str) -> Optional[int]:
        """
        Attempts to find a team ID by searching through nested upcoming matches.
        """
        leagues = self.get_upcoming_matches()
        search_name = team_name.lower().replace("fc ", "").replace(" real", "").strip()
        
        for league in leagues:
            for stage in league.get('stage', []):
                for match in stage.get('matches', []):
                    teams = match.get('teams', {})
                    home = teams.get('home', {})
                    away = teams.get('away', {})
                    if search_name in home.get('name', '').lower():
                        return home.get('id')
                    if search_name in away.get('name', '').lower():
                        return away.get('id')
        return None

    def find_match_id(self, team1_name: str, team2_name: str) -> Optional[int]:
        """
        Attempts to find a match ID for two teams in the nested fixture list.
        """
        leagues = self.get_upcoming_matches()
        t1 = team1_name.lower().replace("fc ", "").replace(" real", "").strip()
        t2 = team2_name.lower().replace("fc ", "").replace(" real", "").strip()
        
        for league in leagues:
            for stage in league.get('stage', []):
                for m in stage.get('matches', []):
                    teams = m.get('teams', {})
                    h = teams.get('home', {}).get('name', '').lower()
                    a = teams.get('away', {}).get('name', '').lower()
                    
                    if (t1 in h and t2 in a) or (t2 in h and t1 in a):
                        return m.get('id')
        return None
