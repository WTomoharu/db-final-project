import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from sqlalchemy.orm import Session
from model import Group, Report, User, WeightRecord

DATABASE_URL = "sqlite:///./data/db.sqlite"
if os.getenv("PYTHON_ENV", "development") == "development":
    DATABASE_URL = "sqlite:///./dev/db.sqlite"

# SQLAlchemyの設定
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# テーブル作成用のSQL文
create_table_querys = [text("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    initial_weight REAL,
    goal_weight REAL
);
"""), text("""
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
"""), text("""
CREATE TABLE IF NOT EXISTS user_group_relations (
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, group_id)
);
"""), text("""
CREATE TABLE IF NOT EXISTS weight_records (
    user_id INTEGER NOT NULL,
    weight REAL NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    PRIMARY KEY (user_id, created_at)
);
"""), text("""
CREATE TABLE IF NOT EXISTS weight_goals (
    user_id INTEGER NOT NULL,
    goal_weight REAL NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    PRIMARY KEY (user_id, created_at)
);
"""), text("""
CREATE TABLE IF NOT EXISTS reports (
    created_at DATETIME NOT NULL,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    weight INT NOT NULL,
    comment TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (group_id) REFERENCES groups (id),
    PRIMARY KEY (created_at, user_id, group_id)
);
""")]

# テーブルを作成
with engine.connect() as connection:
    for create_table_query in create_table_querys:
        connection.execute(create_table_query)

# データベースセッションを取得する依存関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ユーザーを取得する関数
def get_user(db: Session, username: str):
    query = text("SELECT * FROM users WHERE username = :username")
    result = db.execute(query, {"username": username}).fetchone()
    if result:
        return User(**result._mapping)

# 全ユーザーを取得する関数
def get_users(db: Session):
    query = text("SELECT * FROM users")
    result = db.execute(query)
    users = [User(**row._mapping) for row in result]
    return users

# ユーザーを追加する関数
def add_user(db: Session, username: str, password: str):
    query = text("INSERT INTO users (username, password) VALUES (:username, :password)")
    db.execute(query, {"username": username, "password": password})
    db.commit()

# ユーザーの目標体重を設定する関数
def set_goal_weight(db: Session, user_id: int, goal_weight: float):
    query = text("UPDATE users SET goal_weight = :goal_weight WHERE id = :user_id")
    db.execute(query, {"goal_weight": goal_weight, "user_id": user_id})
    db.commit()

# グループを追加する関数
def add_group(db: Session, name: str):
    query = text("INSERT INTO groups (name) VALUES (:name)")
    result = db.execute(query, {"name": name})
    db.commit()
    return {"id": result.lastrowid, "name": name}

# ユーザーをグループに追加する関数
def add_user_to_group(db: Session, user_id: int, group_id: int):
    query = text("INSERT INTO user_group_relations (user_id, group_id) VALUES (:user_id, :group_id)")
    db.execute(query, {"user_id": user_id, "group_id": group_id})
    db.commit()
    return {"user_id": user_id, "group_id": group_id}

# グループを取得する関数
def get_groups(db: Session):
    query = text("SELECT * FROM groups")
    result = db.execute(query)
    groups = [Group(**row._mapping) for row in result]
    return groups

# グループをIDから取得する関数
def get_group_by_id(db: Session, group_id: int):
    query = text("SELECT * FROM groups WHERE id = :group_id")
    result = db.execute(query, {"group_id": group_id}).fetchone()
    if result:
        return Group(**result._mapping)
    return None

# 自分の所属しているグループを取得する関数
def get_user_groups(db: Session, user_id: int):
    query = text("""
        SELECT g.id, g.name
        FROM groups g
        INNER JOIN user_group_relations ugr ON g.id = ugr.group_id
        WHERE ugr.user_id = :user_id
    """)
    result = db.execute(query, {"user_id": user_id})
    groups = [Group(**row._mapping) for row in result]
    return groups

# ユーザーがグループに所属しているか確認する関数
def get_is_meber_of_group(db: Session, user_id: int, group_id: int):
    query = text("""
        SELECT COUNT(*) > 0
        FROM user_group_relations
        WHERE user_id = :user_id AND group_id = :group_id
    """)
    result = db.execute(query, {"user_id": user_id, "group_id": group_id}).scalar()
    return result

# グループを削除する関数
def delete_group(db: Session, group_id: int):
    query = text("DELETE FROM groups WHERE id = :group_id")
    db.execute(query, {"group_id": group_id})
    db.commit()

# 体重記録を追加する関数
def add_weight_record(db: Session, user_id: int, weight: float, created_at: str):
    query = text("INSERT INTO weight_records (user_id, weight, created_at) VALUES (:user_id, :weight, :created_at)")
    db.execute(query, {"user_id": user_id, "weight": weight, "created_at": created_at})
    db.commit()

# ユーザーの体重記録を取得する関数
def get_weight_records(db: Session, user_id: int):
    query = text("SELECT * FROM weight_records WHERE user_id = :user_id")
    result = db.execute(query, {"user_id": user_id})
    records = [WeightRecord(**row._mapping) for row in result]
    return records

# ユーザーの最新の体重記録を取得する関数
def get_latest_weight_record(db: Session, user_id: int):
    query = text("""
        SELECT *
        FROM weight_records
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        LIMIT 1
    """)
    result = db.execute(query, {"user_id": user_id}).fetchone()
    if result:
        return WeightRecord(**result._mapping)
    return None

# グループに体重記録を追加する関数
def add_report(db: Session, user_id: int, group_id: int, weight: float, comment: str | None, created_at: str):
    query = text("""
        INSERT INTO reports (created_at, user_id, group_id, weight, comment)
        VALUES (:created_at, :user_id, :group_id, :weight, :comment)
    """)
    db.execute(query, {
        "created_at": created_at,
        "user_id": user_id,
        "group_id": group_id,
        "weight": weight,
        "comment": comment
    })
    db.commit()

# グループの体重記録を取得する関数
def get_reports_by_group_id(db: Session, group_id: int):
    query = text("""
        SELECT *
        FROM reports r
        JOIN users u ON r.user_id = u.id
        WHERE r.group_id = :group_id
        ORDER BY r.created_at DESC
    """)
    result = db.execute(query, {"group_id": group_id})
    reports = [Report(**row._mapping) for row in result]
    print("get reports", reports)
    return reports