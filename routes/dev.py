from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dev")
async def dev_page(request: Request):
    username = request.session.get("username")
    if username:
        return templates.TemplateResponse("dev.html", {"request": request, "title": f"Welcome {username}"})
    return templates.TemplateResponse("dev.html", {"request": request, "title": "Please log in"})
