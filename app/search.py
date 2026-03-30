import logging
import asyncio
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

async def search_sector_news(sector: str, max_results: int = 5) -> list[dict]:
    """
    Async wrapper for fetching sector news using DuckDuckGo.
    Runs blocking I/O in a thread to avoid blocking FastAPI event loop.
    """
    query = f"{sector} India trade market opportunities 2026"

    def _search():
        results = []
        with DDGS() as ddgs:
            raw = ddgs.text(query, max_results=max_results)
            for item in raw:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", "")
                })
        return results

    try:
        # Run blocking code in a separate thread
        return await asyncio.to_thread(_search)

    except Exception as e:
        logger.warning(f"Search failed for '{sector}': {e}")
        return []

