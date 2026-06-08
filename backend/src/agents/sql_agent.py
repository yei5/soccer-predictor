from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from ..config.prompts import SQL_AGENT_PROMPT
from ..config.settings import settings


class SQLAgent:
  def __init__(self, api_key: Optional[str] = None):
    self.api_key = api_key or settings.GROQ_API_KEY
    self.llm = ChatGroq(
      model=settings.GROQ_MODEL,
      groq_api_key=self.api_key,
      temperature=0.0,
    )
    self.system_prompt = SQL_AGENT_PROMPT

  def generate_query(self, natural_language_query: str) -> str:
    messages = [
      SystemMessage(content=self.system_prompt),
      HumanMessage(content=f"USER REQUEST: {natural_language_query}\n\nSQL QUERY:"),
    ]
    try:
      response = self.llm.invoke(messages)
      return response.content.strip().replace("```sql", "").replace("```", "")
    except Exception as exc:
      return f"Error: {exc}"
