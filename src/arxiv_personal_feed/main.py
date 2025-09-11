from fastapi import FastAPI, Request, Form, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, delete, desc
from .database import engine, create_db_and_tables
from .models import Article, Interest, Category
from .arxiv_fetcher import fetch_new_articles
from .llm_classifier import classify_and_update_articles
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def startup_event():
    create_db_and_tables()
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_classify, "interval", days=1)
    scheduler.start()


def fetch_and_classify():
    logger.info("Starting background task: fetch_and_classify")
    with Session(engine) as session:
        categories = session.exec(select(Category)).all()
        interests = session.exec(select(Interest)).all()
        
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
    session.exec(delete(Interest))
    session.exec(delete(Category))
    session.commit()

    # Add new interests and categories from the form
    new_interests = [Interest(text=i.strip()) for i in interests.splitlines() if i.strip()]
    new_categories = [Category(name=c.strip()) for c in categories.splitlines() if c.strip()]
    
    session.add_all(new_interests)
    session.add_all(new_categories)
    session.commit()

    logger.info("Interests and categories updated. Triggering background fetch.")
    background_tasks.add_task(fetch_and_classify)
    return RedirectResponse(url="/interests", status_code=303)

def run():
    import uvicorn
    uvicorn.run("arxiv_personal_feed.main:app", host="0.0.0.0", port=8000, reload=True)
