import arxiv
from sqlmodel import Session, select
from .database import engine
from .models import Article
import datetime


def fetch_new_articles(categories: list[str]) -> list[Article]:
    search = arxiv.Search(
        query=" OR ".join(f"cat:{cat}" for cat in categories),
        max_results=100,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    new_articles = []
    with Session(engine) as session:
        # Get all existing entry_ids in one query for efficiency
        existing_entry_ids = set(
            session.exec(select(Article.entry_id)).all()
        )

        for result in search.results():
            if result.entry_id in existing_entry_ids:
                continue

            article = Article(
                entry_id=result.entry_id,
                title=result.title,
                abstract=result.summary,
                published=result.published.date(),
            )
            new_articles.append(article)
            
    return new_articles
