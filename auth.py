from fastapi import Request, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import get_user, get_db
from model import User

class Auth(BaseModel):
    user: User

def get_auth(request: Request, db: Session = Depends(get_db)) -> Auth:
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = get_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    auth = Auth(user=user)
    return auth
