# Pydanticモデルの定義
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    username: str
    password: str
    initial_weight: float | None = None
    goal_weight: float | None = None

    model_config = ConfigDict(from_attributes=True)

class Group(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class UserGroupRelation(BaseModel):
    user_id: int
    group_id: int

    model_config = ConfigDict(from_attributes=True)

class WeightRecord(BaseModel):
    user_id: int
    weight: float
    created_at: str

    model_config = ConfigDict(from_attributes=True)

class Report(BaseModel):
    user_id: int
    group_id: int
    weight: float
    comment: str | None
    created_at: str