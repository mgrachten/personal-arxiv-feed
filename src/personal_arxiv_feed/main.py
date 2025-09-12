from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, delete, desc
from .database import engine, create_db_and_tables
from .models import Article, Interest, Category
from .arxiv_fetcher import fetch_new_articles
from .llm_classifier import classify_and_update_articles
from .config import settings
from .cache import LAST_QUERY_ENTRY_IDS
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
import pytz
import datetime
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def startup_event():
    create_db_and_tables()

    # Run once on startup in a separate thread
    import threading

    threading.Thread(target=fetch_and_classify).start()

    executors = {"default": ThreadPoolExecutor(1)}
    scheduler = BackgroundScheduler(timezone=pytz.utc, executors=executors)

    et = pytz.timezone(settings.scheduler_timezone)
    scheduler.add_job(
        fetch_and_classify,
        trigger=CronTrigger(
            hour=settings.scheduler_hour, minute=settings.scheduler_minute, timezone=et
        ),
    )
    scheduler.start()


def fetch_and_classify():
    logger.info("Starting background task: fetch_and_classify")
    with Session(engine) as session:
        categories = session.exec(select(Category)).all()
        interests = list(session.exec(select(Interest)).all())

        if not categories:
            logger.info("No categories defined. Skipping fetch.")
            return

        logger.info(f"Found {len(categories)} categories and {len(interests)} interests.")

        new_articles = fetch_new_articles([c.name for c in categories])
        logger.info(f"Fetched {len(new_articles)} new articles from Arxiv.")

        if new_articles:
            logger.info("Starting classification...")
            classify_and_update_articles(new_articles, interests)
            logger.info("Classification finished.")
    logger.info("Background task finished.")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, session: Session = Depends(get_session)):
    one_month_ago = datetime.date.today() - datetime.timedelta(days=30)
    statement = (
        select(Article)
        .where(Article.published >= one_month_ago, Article.is_relevant == True)
        .order_by(desc(Article.published))
    )
    articles = session.exec(statement).all()

    articles_by_date = {}
    for article in articles:
        if article.published not in articles_by_date:
            articles_by_date[article.published] = []
        articles_by_date[article.published].append(article)

    return templates.TemplateResponse(
        "index.html", {"request": request, "articles_by_date": articles_by_date}
    )


@app.get("/interests", response_class=HTMLResponse)
def read_interests(request: Request, session: Session = Depends(get_session)):
    interests = session.exec(select(Interest)).all()
    categories = session.exec(select(Category)).all()
    return templates.TemplateResponse(
        "interests.html",
        {"request": request, "interests": interests, "categories": categories},
    )


@app.post("/interests")
def update_interests(
    request: Request,
    background_tasks: BackgroundTasks,
    interests: str = Form(""),
    categories: str = Form(""),
    session: Session = Depends(get_session),
):
    # Clear existing interests and categories
    for interest in session.exec(select(Interest)).all():
        session.delete(interest)
    for category in session.exec(select(Category)).all():
        session.delete(category)
    session.commit()

    # Add new interests and categories from the form
    new_interests = [
        Interest(text=i.strip()) for i in interests.splitlines() if i.strip()
    ]
    new_categories = [
        Category(name=c.strip()) for c in categories.splitlines() if c.strip()
    ]

    session.add_all(new_interests)
    session.add_all(new_categories)
    session.commit()

    # Clear the cache to force re-classification
    LAST_QUERY_ENTRY_IDS.clear()
    logger.info("Interests updated, cache cleared.")

    logger.info("Interests and categories updated. Triggering background fetch.")
    background_tasks.add_task(fetch_and_classify)
    return RedirectResponse(url="/interests", status_code=303)


def run():
    import uvicorn

    uvicorn.run(
        "personal_arxiv_feed.main:app",
        host="0.0.0.0",
        port=settings.server_port,
        reload=True,
    )
