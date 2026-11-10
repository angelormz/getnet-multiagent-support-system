import logging
import time

from ddgs import DDGS
from ddgs.exceptions import DDGSException


logger = logging.getLogger(__name__)


def search_web(
    query: str,
    max_results: int = 3,
) -> list[dict]:


    if not query.strip() or max_results < 1:
        return []

    for attempt in range(2):
        try:
            with DDGS(timeout=15) as search:
                results = search.text(
                    query,
                    max_results=max_results,
                )

            normalized = []

            for result in results:
                url = result.get("href", "")
                title = result.get("title", "")
                snippet = result.get("body", "")

                if not url or not snippet:
                    continue

                normalized.append(
                    {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                    }
                )

            if normalized:
                return normalized

            logger.warning(
                "Web search returned no usable results"
            )

        except DDGSException as error:
            logger.warning(
                "Web search attempt %s failed: %s",
                attempt + 1,
                error,
            )

        if attempt == 0:
            time.sleep(1)

    return []
