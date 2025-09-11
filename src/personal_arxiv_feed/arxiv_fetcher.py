import arxiv
from sqlmodel import Session, select
from .database import engine
from .models import Article
from .config import settings
import datetime


def fetch_new_articles(categories: list[str]) -> list[Article]:
    """
    Fetches new articles for each category since the last update.
    """
    new_articles_map = {}

    with Session(engine) as session:
        # Get all existing entry_ids in one query for efficiency
        existing_entry_ids = set(session.exec(select(Article.entry_id)).all())

        for category in categories:
            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=settings.arxiv_max_results_per_category,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )

            for result in search.results():
                if (
                    result.entry_id in existing_entry_ids
                    or result.entry_id in new_articles_map
                ):
                    continue

                article = Article(
                    entry_id=result.entry_id,
                    title=result.title,
                    abstract=result.summary,
                    published=result.published.date(),
                )
                new_articles_map[result.entry_id] = article

    return list(new_articles_map.values())
