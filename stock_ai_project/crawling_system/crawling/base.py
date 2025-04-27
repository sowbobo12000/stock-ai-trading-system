from abc import ABC, abstractmethod

class BaseNewsCrawler(ABC):
    def __init__(self, symbol: str):
        self.symbol = symbol.upper()

    @abstractmethod
    def fetch_articles(self) -> list[dict]:
        """
        Return a list of articles:
        [
            {"title": "...", "content": "...", "source": "Yahoo", "published_at": datetime, "symbol": "TSLA"},
            ...
        ]
        """
        pass
