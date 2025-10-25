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


@app.get("/todos", response_model=list[Todo])
def list_todos(completed: bool | None = None, db: sqlite3.Connection = Depends(get_db)):
    if completed is None:
        rows = db.execute("SELECT * FROM todos ORDER BY id").fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM todos WHERE completed = ? ORDER BY id", (completed,)
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return dict(row)


@app.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoInput, db: sqlite3.Connection = Depends(get_db)):
    with db:
        cursor = db.execute(
            "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
            (todo.title, todo.description, todo.completed),
        )
        result = get_todo(cursor.lastrowid, db)
    return result


@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: TodoInput, db: sqlite3.Connection = Depends(get_db)):
    with db:
        cursor = db.execute(
            "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
            (todo.title, todo.description, todo.completed, todo_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        result = get_todo(todo_id, db)
    return result


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: sqlite3.Connection = Depends(get_db)):
    with db:
        cursor = db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)