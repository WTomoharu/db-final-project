from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from auth import Auth, get_auth
from db import add_group, add_report, get_group_by_id, add_user_to_group, get_is_meber_of_group, get_reports_by_group_id, get_user_groups, get_db, delete_group, get_weight_records, get_latest_weight_record
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def date_to_str(date: str):
    return datetime.fromisoformat(date).strftime("%Y-%m-%d %H:%M")

@router.get("/groups")
async def list_my_groups(request: Request, db: Session = Depends(get_db), auth: Auth = Depends(get_auth)):
    user_groups = get_user_groups(db, auth.user.id)
    return templates.TemplateResponse("group.html", {"request": request, "groups": user_groups})

@router.get("/groups/create")
async def create_group_form(request: Request):
    return templates.TemplateResponse("group_create.html", {"request": request})

@router.post("/groups/create")
async def create_group(name: str = Form(), db: Session = Depends(get_db), auth: Auth = Depends(get_auth)):
    group = add_group(db, name)
    add_user_to_group(db, auth.user.id, group["id"])
    return RedirectResponse(url="/groups", status_code=302)

@router.get("/groups/{group_id}")
async def group_detail(request: Request, group_id: int, db: Session = Depends(get_db), auth: Auth = Depends(get_auth)):
    group = get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    is_member = get_is_meber_of_group(db, auth.user.id, group_id)

    reports = get_reports_by_group_id(db, group_id)

    return templates.TemplateResponse("group_detail.html", {"request": request, "group": group, "is_member": is_member, "url_root": request.base_url, "reports": reports, "date_to_str": date_to_str})

@router.post("/groups/{group_id}/join")
async def join_user_to_group_endpoint(request: Request, group_id: int, db: Session = Depends(get_db), auth: Auth = Depends(get_auth)):
    add_user_to_group(db, auth.user.id, group_id)
    return RedirectResponse(url=f"/groups/{group_id}", status_code=302)

@router.post("/groups/{group_id}/delete")
async def delete_group_endpoint(group_id: int, db: Session = Depends(get_db), auth: Auth = Depends(get_auth)):
    group = get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    is_member = get_is_meber_of_group(db, auth.user.id, group_id)
    if not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to delete this group")

    delete_group(db, group_id)
    return RedirectResponse(url="/groups", status_code=302)

@router.post("/groups/{group_id}/weights")
async def add_weight_record(group_id: int, comment = Form(), db: Session = Depends(get_db), auth: Auth = Depends(get_auth)):
    group = get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    is_member = get_is_meber_of_group(db, auth.user.id, group_id)
    if not is_member:
        raise HTTPException(status_code=403, detail="Not authorized to add weight to this group")
    
    weight_record = get_latest_weight_record(db, auth.user.id)
    if not weight_record:
        raise HTTPException(status_code=404, detail="No weight record found for user")
    
    JST = timezone(timedelta(hours=9))
    created_at = datetime.now(JST).isoformat()

    if not comment:
        comment = None

    add_report(db, user_id=auth.user.id, group_id=group_id, weight=weight_record.weight, comment=comment, created_at=created_at)

    return RedirectResponse(url=f"/groups/{group_id}", status_code=302)
