import arxiv
from .models import Article
from .config import settings
from .cache import LAST_QUERY_ENTRY_IDS
import logging

logger = logging.getLogger(__name__)


def fetch_new_articles(categories: list[str]) -> list[Article]:
    """
    Fetches new articles for each category, avoiding duplicates from the last query.
    """
    new_articles_map = {}
    current_query_ids = set()

    for category in categories:
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=settings.arxiv_max_results_per_category,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

        for result in search.results():
            current_query_ids.add(result.entry_id)
            if (
                result.entry_id in LAST_QUERY_ENTRY_IDS
                or result.entry_id in new_articles_map
            ):
                continue

            article = Article(
                entry_id=result.entry_id,
                title=result.title,
                authors=", ".join(author.name for author in result.authors),
                abstract=result.summary,
                published=result.published.date(),
            )
            new_articles_map[result.entry_id] = article

    # Update the global cache with the IDs from this query
    LAST_QUERY_ENTRY_IDS.clear()
    LAST_QUERY_ENTRY_IDS.update(current_query_ids)
    logger.info(f"Cache updated with {len(LAST_QUERY_ENTRY_IDS)} entry IDs.")

    return list(new_articles_map.values())
