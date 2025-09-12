import logging
import asyncio

from pydantic import BaseModel, Field
from sqlmodel import Session, select
import pydantic_ai

from .models import Article, Interest
from .config import settings
from .database import engine


logger = logging.getLogger(__name__)


class RelevanceDecision(BaseModel):
    is_relevant: bool = Field(
        ..., description="Whether the article is relevant to the user's interests."
    )
    reason: str = Field(..., description="A short reason for the decision.")


class BatchRelevanceDecision(BaseModel):
    decisions: list[RelevanceDecision]


async def classify_article_batch(
    articles: list[Article], interests: list[Interest]
) -> list[RelevanceDecision]:
    interest_str = ", ".join([i.text for i in interests])

    instructions = f"You are a research assistant. Your task is to determine if a research paper is relevant to the user's interests. The user's interests are: {interest_str}. You will be given a list of papers and you must return a decision for each paper."

    papers_str = ""
    for i, article in enumerate(articles):
        papers_str += f"\n--- Paper {i + 1} ---\n"
        for field in settings.llm_fields_to_include:
            # Ensure authors are included if specified
            if field == "authors" and not hasattr(article, "authors"):
                continue
            papers_str += f"{field.capitalize()}: {getattr(article, field)}\n"

    user_prompt = f"""
    Here are {len(articles)} research papers:
    {papers_str}

    Are these papers relevant to my interests?
    """

    agent = pydantic_ai.Agent(
        instructions=instructions,
        retries=3,
        output_type=BatchRelevanceDecision,
    )

    result = await agent.run(user_prompt=user_prompt, model=settings.llm_model)
    return result.output.decisions


def classify_and_update_articles(articles: list[Article], interests: list[Interest]):
    if not articles:
        return

    if not interests:
        logger.info("No interests provided. Skipping classification.")
        return

    all_decisions = []
    try:
        logger.info(
            f"Classifying {len(articles)} articles in batches of {settings.llm_batch_size}..."
        )
        for i in range(0, len(articles), settings.llm_batch_size):
            batch = articles[i : i + settings.llm_batch_size]
            logger.info(f"Classifying batch {i // settings.llm_batch_size + 1}...")
            decisions = asyncio.run(classify_article_batch(batch, interests))
            all_decisions.extend(decisions)
        logger.info("Finished classifying all articles.")
    except Exception as e:
        logger.error(
            f"An error occurred during article classification: {e}", exc_info=True
        )
        return

    with Session(engine) as session:
        # Final check to prevent race conditions
        article_ids_to_check = [article.entry_id for article in articles]
        existing_ids = set(
            session.exec(
                select(Article.entry_id).where(Article.entry_id.in_(article_ids_to_check))
            ).all()
        )

        saved_count = 0
        for article, decision in zip(articles, all_decisions):
            if decision.is_relevant and article.entry_id not in existing_ids:
                article.is_relevant = decision.is_relevant
                article.relevance_reason = decision.reason
                session.add(article)
                saved_count += 1

        if saved_count > 0:
            session.commit()
            logger.info(
                f"Successfully saved {saved_count} new relevant articles to the database."
            )
        else:
            logger.info("No new relevant articles to save.")
