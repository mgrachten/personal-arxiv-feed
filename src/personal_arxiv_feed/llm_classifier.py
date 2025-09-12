from pydantic import BaseModel, Field
import pydantic_ai
from .models import Article, Interest
from .config import settings
from sqlmodel import Session
from .database import engine
import logging

logger = logging.getLogger(__name__)


class RelevanceDecision(BaseModel):
    is_relevant: bool = Field(
        ..., description="Whether the article is relevant to the user's interests."
    )
    reason: str = Field(..., description="A short reason for the decision.")


class BatchRelevanceDecision(BaseModel):
    decisions: list[RelevanceDecision]


def classify_article_batch(
    articles: list[Article], interests: list[Interest]
) -> list[RelevanceDecision]:
    interest_str = ", ".join([i.text for i in interests])

    instructions = f"You are a research assistant. Your task is to determine if a research paper is relevant to the user's interests. The user's interests are: {interest_str}. You will be given a list of papers and you must return a decision for each paper."

    papers_str = ""
    for i, article in enumerate(articles):
        papers_str += f"\n--- Paper {i + 1} ---\n"
        for field in settings.llm_fields_to_include:
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

    result = agent.run_sync(user_prompt=user_prompt, model=settings.llm_model)
    return result.output.decisions


def classify_and_update_articles(articles: list[Article], interests: list[Interest]):
    if not interests:
        logger.info("No interests provided. Marking all new articles as relevant.")
        with Session(engine) as session:
            for article in articles:
                article.is_relevant = True
                article.relevance_reason = (
                    "No interests provided, defaulting to relevant."
                )
                session.add(article)
            session.commit()
        return

    all_decisions = []
    try:
        logger.info(
            f"Classifying {len(articles)} articles in batches of {settings.llm_batch_size}..."
        )
        for i in range(0, len(articles), settings.llm_batch_size):
            batch = articles[i : i + settings.llm_batch_size]
            logger.info(f"Classifying batch {i // settings.llm_batch_size + 1}...")
            decisions = classify_article_batch(batch, interests)
            all_decisions.extend(decisions)
        logger.info("Finished classifying all articles.")
    except Exception as e:
        logger.error(
            f"An error occurred during article classification: {e}", exc_info=True
        )
        return

    with Session(engine) as session:
        for article, decision in zip(articles, all_decisions):
            session.add(article)
            article.is_relevant = decision.is_relevant
            article.relevance_reason = decision.reason
        session.commit()
        logger.info(
            f"Successfully saved {len(all_decisions)} classified articles to the database."
        )
