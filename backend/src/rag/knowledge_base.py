SOCCER_KNOWLEDGE_DOCUMENTS = [
  {
    "topic": "home_advantage",
    "content": (
      "Home advantage in top European leagues typically adds 0.3-0.5 expected goals "
      "and increases home win probability by 8-12%. Crowd support, travel fatigue, "
      "and familiarity with the pitch are key drivers."
    ),
  },
  {
    "topic": "form_analysis",
    "content": (
      "Recent form over the last 5 matches is a strong short-term signal. Weight wins "
      "against stronger opponents more heavily. A team on a 4+ match unbeaten run "
      "often shows improved confidence and defensive organization."
    ),
  },
  {
    "topic": "injuries",
    "content": (
      "Missing key strikers reduces expected goals by 0.2-0.4 per game. Absence of "
      "central defenders increases conceding probability. Always cross-check projected "
      "lineups with official injury reports before finalizing predictions."
    ),
  },
  {
    "topic": "head_to_head",
    "content": (
      "Head-to-head history matters most when tactical styles clash repeatedly. "
      "Weight the last 3 H2H meetings at 60%, older meetings at 40%. Derby matches "
      "often deviate from league-table expectations due to psychological factors."
    ),
  },
  {
    "topic": "draw_probability",
    "content": (
      "Draw probability rises when teams are closely matched in league position (within "
      "3 places), both have strong defenses (low goals conceded average), or both are "
      "on unbeaten runs. Typical draw rates: Serie A ~27%, Premier League ~24%, La Liga ~25%."
    ),
  },
  {
    "topic": "xg_regression",
    "content": (
      "Teams overperforming their expected goals (xG) tend to regress toward the mean. "
      "If a team wins frequently with low shot quality, reduce future win probability slightly."
    ),
  },
  {
    "topic": "fixture_congestion",
    "content": (
      "Teams playing European competitions midweek often rotate squads in domestic leagues. "
      "Check if a team played within 72 hours before the match — fatigue reduces pressing intensity."
    ),
  },
  {
    "topic": "weather",
    "content": (
      "Heavy rain and strong wind favor defensive, low-scoring games. Extreme heat (>32°C) "
      "reduces total running distance and can favor technically superior teams with deeper squads."
    ),
  },
  {
    "topic": "relegation_battle",
    "content": (
      "Teams fighting relegation in the final 8 matchdays show elevated motivation at home "
      "but may collapse away. Mid-table teams with nothing to play for can underperform."
    ),
  },
  {
    "topic": "prediction_calibration",
    "content": (
      "Well-calibrated predictions should sum probabilities to 1.0. Avoid extreme "
      "confidence (>75%) unless multiple independent signals align: form, H2H, standings, "
      "and absence of key injuries all point the same direction."
    ),
  },
]


class KnowledgeBase:
  def __init__(self):
    self.documents = SOCCER_KNOWLEDGE_DOCUMENTS

  def get_all(self):
    return [f"[{doc['topic']}] {doc['content']}" for doc in self.documents]

  def get_by_topics(self, topics: list[str]) -> list[str]:
    selected = [doc for doc in self.documents if doc["topic"] in topics]
    return [f"[{doc['topic']}] {doc['content']}" for doc in selected]
