from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from auth import Auth, get_auth
from db import get_user, add_user, get_db, set_goal_weight
from sqlalchemy import text
from fastapi.templating import Jinja2Templates
import secrets

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    user = get_user(db, username)
    if not user or not secrets.compare_digest(user.password, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    request.session["username"] = username
    return RedirectResponse(url="/", status_code=302)

@router.get("/signup")
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
async def signup(username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    existing_user = get_user(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    add_user(db, username, password)
    return RedirectResponse(url="/login", status_code=302)

@router.post("/logout")
@router.get("/logout")
async def logout_redirect(request: Request):
    if not request.session.get("username"):
        return RedirectResponse(url="/login", status_code=302)
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@router.get("/me")
async def me_page(request: Request, auth: Auth = Depends(get_auth)):
    return templates.TemplateResponse("me.html", {"request": request, "user": auth.user})

@router.post("/me/goal_weight")
async def change_goal_weight(request: Request, goal_weight: float = Form(), db: Session = Depends(get_db), auth: Auth = Depends(get_auth)):
    if goal_weight <= 0:
        raise HTTPException(status_code=400, detail="Target weight must be greater than 0")
    
    set_goal_weight(db, auth.user.id, goal_weight)
    return RedirectResponse(url="/me", status_code=302)
