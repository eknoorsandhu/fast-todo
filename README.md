# fast-todo

A small to-do REST API using FastAPI and SQLite. No frontend, just JSON.

## Run it

You'll need Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync --locked
uv run uvicorn main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Open `/docs` to try requests in
your browser, or use curl. The OpenAPI spec is at `/openapi.json`.

The app creates its table on startup and saves everything in `todo.db`
beside `main.py`. Restarting the server won't clear your tasks.
The database is local data, so it's ignored by Git.

To use a different database file, set `TODO_DB_PATH` before starting:

```sh
TODO_DB_PATH=/tmp/my-todos.db uv run uvicorn main:app --reload
```

The parent folder must already exist.

## Routes

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/` | Quick welcome message |
| GET | `/todos` | List all tasks, oldest ID first |
| GET | `/todos?completed=true` | List finished tasks; use `false` for unfinished ones |
| GET | `/todos/{id}` | Get one task |
| POST | `/todos` | Add a task; returns `201` |
| PUT | `/todos/{id}` | Replace a task |
| DELETE | `/todos/{id}` | Delete a task; returns `204` with no body |

Each task has an integer `id`, a `title`, a `description`, and a `completed` flag.
The server assigns the ID. Titles are required, trimmed, and must be 1–200
characters. Descriptions are trimmed and can be up to 2,000 characters.
Description defaults to `""` and completed defaults to `false`.

`PUT` replaces the task, so send the title even when just marking it done.
Leaving out description or completed resets them to their defaults.
Missing tasks return `404`; invalid request data returns `422`.

## Try it

Create a task:

```sh
curl -X POST http://127.0.0.1:8000/todos \
  -H 'Content-Type: application/json' \
  -d '{"title":"Do homework","description":"Finish the math worksheet"}'
```

Example response from a fresh database:

```json
{"title":"Do homework","description":"Finish the math worksheet","completed":false,"id":1}
```

List tasks, finish the first one, then delete it:

```sh
curl http://127.0.0.1:8000/todos

curl -X PUT http://127.0.0.1:8000/todos/1 \
  -H 'Content-Type: application/json' \
  -d '{"title":"Do homework","description":"Finish the math worksheet","completed":true}'

curl -X DELETE http://127.0.0.1:8000/todos/1
```

Use the ID returned by your own create request if it isn't `1`.

This is a local practice app without login or user accounts. Everyone using the
same server shares the same tasks; don't expose it publicly as-is.
