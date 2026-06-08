import re
from typing import Tuple

class InputValidator:
    @staticmethod
    def validate_team_name(name: str) -> bool:
        """Simple validation for team names to prevent weird characters."""
        if not name:
            return False
        return bool(re.match(r"^[a-zA-Z0-9\s\-\.]+$", name))

class SQLValidator:
    @staticmethod
    def is_safe_query(query: str) -> Tuple[bool, str]:
        """Checks if a SQL query is a simple SELECT and doesn't contain dangerous keywords."""
        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]
        query_upper = query.upper()
        
        if not query_upper.strip().startswith("SELECT"):
            return False, "Only SELECT queries are allowed."
            
        for kw in dangerous_keywords:
            if kw in query_upper:
                return False, f"Dangerous keyword '{kw}' detected."
                
        return True, ""
