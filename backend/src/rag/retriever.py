from typing import List

from ..utils.logger import logger
from .knowledge_base import KnowledgeBase


class Retriever:
  """Keyword-based retriever (Groq does not provide an embeddings API)."""

  def __init__(self):
    self.kb = KnowledgeBase()
    self._docs = self.kb.get_all()
    logger.info("Initialized keyword RAG retriever for soccer knowledge.")

  def retrieve(self, query: str, k: int = 4) -> List[str]:
    query_words = [w for w in query.lower().split() if len(w) > 3]
    scored = []
    for doc in self._docs:
      score = sum(1 for word in query_words if word in doc.lower())
      if score:
        scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in scored[:k]] or self._docs[:k]
