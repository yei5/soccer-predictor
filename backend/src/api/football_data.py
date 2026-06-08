import os
import requests
import time
from typing import Optional, Dict, Any, List
from ..config.settings import settings

class FootballDataClient:
    BASE_URL = "https://api.football-data.org/v4"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FOOTBALL_DATA_API_KEY
        if not self.api_key:
            raise ValueError("FOOTBALL_DATA_API_KEY not found in environment or passed as argument.")
        
        self.api_key = self.api_key.strip()
        
        self.headers = {
            "X-Auth-Token": self.api_key
        }
        self.last_request_time = 0
        self.min_interval = 6.0  # 10 requests per minute = 1 request every 6 seconds

    def _wait_for_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._wait_for_rate_limit()
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 429:
            # Rate limit hit, wait longer and retry once
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limit exceeded. Waiting for {retry_after} seconds...")
            time.sleep(retry_after)
            return self._make_request(endpoint, params)
            
        response.raise_for_status()
        return response.json()

    def get_competitions(self) -> List[Dict[str, Any]]:
        """Fetch all available competitions."""
        data = self._make_request("competitions")
        # Filter for the 12 free tier competitions if needed, 
        # or just return all and let the UI handle it.
        return data.get("competitions", [])

    def get_teams(self, competition_id: str) -> List[Dict[str, Any]]:
        """Fetch teams for a specific competition."""
        data = self._make_request(f"competitions/{competition_id}/teams")
        return data.get("teams", [])

    def get_standings(self, competition_id: str) -> List[Dict[str, Any]]:
        """Fetch current standings for a competition."""
        data = self._make_request(f"competitions/{competition_id}/standings")
        return data.get("standings", [])

    def get_team_matches(self, team_id: int, status: str = "FINISHED", limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch recent matches for a team."""
        params = {"status": status, "limit": limit}
        data = self._make_request(f"teams/{team_id}/matches", params=params)
        return data.get("matches", [])

    def get_head_to_head(self, team1_id: int, team2_id: int) -> Dict[str, Any]:
        """Fetch H2H data between two teams by searching through a wider match history."""
        # Fetch a larger window of matches (last 100) to find cross-competition encounters
        params = {"limit": 100} 
        data = self._make_request(f"teams/{team1_id}/matches", params=params)
        matches = data.get("matches", [])
        
        # Filter for encounters with team2
        h2h_matches = [
            m for m in matches 
            if (m['homeTeam']['id'] == team2_id or m['awayTeam']['id'] == team2_id)
            and m['status'] == 'FINISHED'
        ]
        
        return {
            "matches": sorted(h2h_matches, key=lambda x: x['utcDate'], reverse=True)[:10] 
        }

    def get_global_team_info(self, team_id: int) -> Dict[str, Any]:
        """Fetch general info about a team, including current active competitions."""
        return self._make_request(f"teams/{team_id}")
