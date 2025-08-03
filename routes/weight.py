from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from db import get_user, get_weight_records, add_weight_record, get_db
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def date_to_str(date: str):
    return datetime.fromisoformat(date).strftime("%Y-%m-%d %H:%M")

@router.get("/weights")
async def list_weight_records(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    weight_records = get_weight_records(db, user.id)
    return templates.TemplateResponse("weights.html", {"request": request, "weight_records": weight_records, "date_to_str": date_to_str})

@router.post("/weights")
async def add_weight_record_endpoint(request: Request, weight: float = Form(), db: Session = Depends(get_db)):
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    JST = timezone(timedelta(hours=9))
    created_at = datetime.now(JST).isoformat()
    add_weight_record(db, user.id, weight, created_at)

    return RedirectResponse(url="/weights", status_code=302)
