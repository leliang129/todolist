from functools import lru_cache
from pathlib import Path
from typing import List
from urllib.parse import quote_plus
import yaml
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = "mysql+pymysql://user:password@127.0.0.1:3306/todo"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_in: int = 86400
    cors_origins: List[str] = ["http://localhost:5173"]
    admin_username: str = "admin"
    admin_password: str = "Admin@123456"
    admin_email: str | None = None


def _load_yaml_config() -> dict:
    root = Path(__file__).resolve().parents[2]
    path = root / "config.yaml"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def _build_database_url(mysql: dict) -> str:
    host = mysql.get("host", "127.0.0.1")
    port = mysql.get("port", 3306)
    username = quote_plus(str(mysql.get("username", "user")))
    password = quote_plus(str(mysql.get("password", "password")))
    database = mysql.get("database", "todo")
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"


@lru_cache
def get_settings() -> Settings:
    data = _load_yaml_config()
    if "mysql" in data and "database_url" not in data:
        data["database_url"] = _build_database_url(data.get("mysql") or {})
    return Settings(**data)
