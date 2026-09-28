import logging
import os
from contextlib import asynccontextmanager

from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user, require_roles
from app.database import get_db, init_database
from app.models import Issue
from app.notifications import notify_issue_status_changed
from app.schemas import IssueCreate, IssueResponse, IssueStatusUpdate
from app.seed import seed_database

SERVICE_NAME = os.getenv("SERVICE_NAME", "utility-service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    from app.database import SessionLocal

    with SessionLocal() as session:
        seed_database(session)
    logger.info("%s started", SERVICE_NAME)
    yield


app = FastAPI(title="Utility Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.post("/issues", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(
    payload: IssueCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Issue:
    issue = Issue(
        id=str(uuid4()),
        user_id=current_user.id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        category=payload.category.strip().upper(),
        address=payload.address.strip(),
        status="NEW",
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    logger.info("issue_created issue_id=%s user_id=%s", issue.id, current_user.id)
    return issue


@app.get("/issues", response_model=list[IssueResponse])
def list_issues(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Issue]:
    query = select(Issue).order_by(Issue.created_at.desc())
    if current_user.role not in {"OPERATOR", "ADMIN"}:
        query = query.where(Issue.user_id == current_user.id)
    return list(db.scalars(query).all())


@app.put("/issues/{issue_id}", response_model=IssueResponse)
def update_issue_status(
    issue_id: str,
    payload: IssueStatusUpdate,
    _: Annotated[CurrentUser, Depends(require_roles("OPERATOR", "ADMIN"))],
    db: Annotated[Session, Depends(get_db)],
) -> Issue:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заявка не найдена")

    issue.status = payload.status
    db.commit()
    db.refresh(issue)
    logger.info("issue_status_updated issue_id=%s status=%s", issue.id, issue.status)
    notify_issue_status_changed(issue.id, issue.user_id, issue.status)
    return issue
