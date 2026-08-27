# Task Manager API

A RESTful task management API built with **FastAPI** and **PostgreSQL**, featuring JWT-based authentication, per-user task ownership, rate limiting, and a Dockerized setup for easy local development.

## Features

- **User authentication** — signup and login with hashed passwords and JWT access tokens
- **Task CRUD** — create, list, retrieve, update, and delete tasks
- **Per-user data isolation** — users can only see and modify their own tasks (403 Forbidden on cross-user access)
- **Rate limiting** — signup and login endpoints are throttled (5 requests/minute) via `slowapi`
- **Pagination** — task listing supports `skip`/`limit` query parameters
- **Dockerized** — API and PostgreSQL run together via Docker Compose
- **Tested** — Pytest suite covering auth flows and task ownership/authorization rules

## Tech Stack

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Framework      | FastAPI                              |
| Database       | PostgreSQL                           |
| ORM            | SQLAlchemy                           |
| Auth           | JWT (python-jose), passlib (bcrypt)  |
| Rate limiting  | slowapi                              |
| Testing        | Pytest, FastAPI TestClient           |
| Containerization | Docker, Docker Compose             |

## Project Structure

```
task-manager-api/
├── main.py              # FastAPI app entrypoint, router registration
├── auth.py              # Password hashing, JWT creation/decoding
├── config.py             # App settings (pydantic-settings)
├── database.py           # SQLAlchemy engine/session setup
├── limiter.py             # slowapi rate limiter config
├── models.py              # SQLAlchemy models (User, Task)
├── schemas.py             # Pydantic request/response schemas
├── users.py                # Auth routes: /signup, /login
├── tasks.py                 # Task CRUD routes
├── tests/                    # Pytest test suite
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## API Endpoints

### Auth

| Method | Endpoint   | Description                          | Rate limit |
|--------|-----------|---------------------------------------|------------|
| POST   | `/signup` | Register a new user                   | 5/min      |
| POST   | `/login`  | Authenticate and receive a JWT token  | 5/min      |

### Tasks

*All task endpoints require a `Bearer` token from `/login`.*

| Method | Endpoint          | Description                          |
|--------|-------------------|----------------------------------------|
| POST   | `/tasks/`          | Create a new task                     |
| GET    | `/tasks/`           | List the current user's tasks (paginated) |
| GET    | `/tasks/{task_id}`  | Get a single task by ID               |
| PUT    | `/tasks/{task_id}`  | Update a task                         |
| DELETE | `/tasks/{task_id}`  | Delete a task                         |

Accessing or modifying a task you don't own returns `403 Forbidden`. Requesting a task that doesn't exist returns `404 Not Found`.

## Getting Started

### Option 1: Run with Docker (recommended)

```bash
git clone https://github.com/vivekyadav4545/task-manager-api.git
cd task-manager-api
```

Create a `.env` file in the project root:

```env
POSTGRES_PASSWORD=your_postgres_password
SECRET_KEY=your_jwt_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Then build and start the containers:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

### Option 2: Run locally

Requires Python 3.12+ and a running PostgreSQL instance.

```bash
git clone https://github.com/vivekyadav4545/task-manager-api.git
cd task-manager-api
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Set up your `.env` file with your local database URL and secret key, then run:

```bash
uvicorn main:app --reload
```

## Running Tests

```bash
pytest -v
```

Tests spin up and tear down a dedicated test database per test function, covering:
- User signup/login flows
- Task creation and listing
- Cross-user access restrictions (403 on unauthorized access)
- 404 handling for nonexistent tasks

## Example Usage

**Sign up:**
```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

**Log in:**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

**Create a task:**
```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Finish README", "description": "Write project docs"}'
```

## License

This project is open source and available for learning and portfolio purposes.
