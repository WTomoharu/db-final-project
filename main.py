from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, Response, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.sessions import SessionMiddleware
import secrets
import os
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from sqlalchemy import text

from db import add_group, add_user, add_user_to_group, get_db, get_groups, get_user, get_users, get_weight_records, add_weight_record, get_user_groups
from model import User
from routes.user import router as user_router
from routes.group import router as group_router
from routes.weight import router as weight_router
from routes.dev import router as dev_router

app = FastAPI()

# Jinja2のテンプレート環境を設定
templates = Jinja2Templates(directory="templates")

# SessionMiddlewareを追加
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "default-secret-key"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    username = request.session.get("username")
    return templates.TemplateResponse("index.html", {"request": request, "title": "アプリ版体重管理", "username": username})



@app.post("/update-goal")
async def update_goal_weight(request: Request, goal_weight: float = Form(), db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = text("UPDATE users SET goal_weight = :goal_weight WHERE id = :user_id")
    db.execute(query, {"goal_weight": goal_weight, "user_id": user.id})
    db.commit()

    return RedirectResponse(url="/", status_code=302)

@app.get("/get-goal")
async def get_goal_weight(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        return {"goal_weight": None}

    user = get_user(db, username)
    if not user:
        return {"goal_weight": None}

    return {"goal_weight": user.goal_weight}

app.include_router(user_router)
app.include_router(group_router)
app.include_router(weight_router)
app.include_router(dev_router)
