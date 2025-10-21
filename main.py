import os
import sqlite3
from contextlib import asynccontextmanager, closing
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field

DB_PATH = Path(os.environ.get("TODO_DB_PATH", Path(__file__).with_name("todo.db")))


@asynccontextmanager
async def lifespan(app: FastAPI):
    with closing(sqlite3.connect(DB_PATH)) as db:
        with db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))
                )
                """
            )
    yield


app = FastAPI(title="Todo API", lifespan=lifespan)


class TodoInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    completed: bool = False


class Todo(TodoInput):
    id: int


def get_db():
    with closing(sqlite3.connect(DB_PATH, check_same_thread=False)) as db:
        db.row_factory = sqlite3.Row
        yield db


@app.get("/")
def root():
    return {"message": "Todo API. Try /docs to use it."}
