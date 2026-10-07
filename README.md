# Task Management API

A RESTful Task Management API built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, and **Pydantic**.

This project was built as a practical backend development project to learn and implement real-world concepts such as API design, database integration, validation, repository pattern, database migrations, automated testing, and clean project structure.

## Features

- Create tasks
- Get all tasks
- Get a task by ID
- Update tasks using PATCH
- Delete tasks
- Request validation with Pydantic
- Strict boolean validation
- PostgreSQL database integration
- SQLAlchemy ORM
- Alembic database migrations
- Repository pattern
- Dependency injection with FastAPI
- Database session management
- Automated API tests with pytest
- Test database isolation
- Database-level testing
- Health check endpoint
- Environment-based configuration

## Tech Stack

- **Python 3.13+**
- **FastAPI**
- **Pydantic**
- **SQLAlchemy**
- **PostgreSQL**
- **Psycopg**
- **Alembic**
- **Pytest**
- **HTTPX**

## Project Structure

```text
Task Management API/
│
├── app/
│   ├── database/
│   │   └── database.py
│   │
│   ├── models/
│   │   └── task.py
│   │
│   ├── repositories/
│   │   └── task_repository.py
│   │
│   ├── routers/
│   │   └── tasks.py
│   │
│   ├── schemas/
│   │   └── task.py
│   │
│   └── main.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── ...
│
├── tests/
│   ├── conftest.py
│   └── test_tasks.py
│
├── .env
├── .gitignore
├── alembic.ini
├── pyproject.toml
└── README.md
```

## API Endpoints

### Health Check

```http
GET /health
```

Returns the health status of the API and checks database connectivity.

### Create Task

```http
POST /tasks/
```

Example request:

```json
{
  "title": "Learn FastAPI",
  "description": "Build a Task Management API"
}
```

### Get All Tasks

```http
GET /tasks/
```

### Get Task by ID

```http
GET /tasks/{task_id}
```

### Update Task

```http
PATCH /tasks/{task_id}
```

Example:

```json
{
  "completed": true
}
```

### Delete Task

```http
DELETE /tasks/{task_id}
```

## Database

The application uses **PostgreSQL** as its database and **SQLAlchemy** as the ORM.

Database schema changes are managed using **Alembic** migrations.

Example migration commands:

```bash
alembic revision --autogenerate -m "create tasks table"
```

```bash
alembic upgrade head
```

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=your_database_connection_string
TEST_DATABASE_URL=your_test_database_connection_string
```

Do not commit `.env` to Git.

The `.gitignore` file already excludes it.

## Installation

Clone the repository:

```bash
git clone https://github.com/Gaurav-backend/Task-Management-API.git
cd task-management-api
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```bash
pip install -e .
```

Install development dependencies if required:

```bash
pip install pytest httpx httpx2
```

## Database Setup

Make sure PostgreSQL is running.

Create the required databases and configure the connection strings in `.env`.

Then run the Alembic migrations:

```bash
alembic upgrade head
```

## Running the Application

Start the development server with:

```bash
fastapi dev app/main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Alternative documentation:

```text
http://127.0.0.1:8000/redoc
```

## Running Tests

Run the complete test suite:

```bash
pytest
```

The project currently contains **37 passing tests** covering CRUD operations, validation, error handling, database persistence, updates, deletion, transaction visibility, and database isolation.

## Testing

The test suite covers:

- Successful task creation
- Retrieving tasks
- Retrieving tasks by ID
- Updating tasks
- Deleting tasks
- Missing resources
- Invalid request data
- Empty and whitespace-only values
- Strict boolean validation
- Partial updates
- Multiple tasks
- Database persistence
- Database updates
- Database deletion
- Transaction commit visibility
- Database isolation
- Health check

## Architecture

The application follows a layered structure:

```text
Client
   ↓
FastAPI Router
   ↓
Pydantic Schema
   ↓
Repository
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

Database sessions are provided through FastAPI dependency injection:

```python
db: Session = Depends(get_db)
```

The repository layer keeps database operations separate from the route handlers.

## Learning Goals

This project was created to gain practical experience with:

- Python backend development
- FastAPI
- REST APIs
- Pydantic validation
- SQLAlchemy ORM
- PostgreSQL
- Database migrations
- Dependency injection
- Repository pattern
- Automated testing
- pytest fixtures
- Database testing
- Clean backend project structure

## Future Improvements

Planned improvements include:

- User registration and authentication
- Password hashing
- JWT authentication
- User-owned tasks
- Protected endpoints
- Pagination
- Filtering and sorting
- Improved error handling
- Docker support
- Production deployment

## Author

**Gaurav Dabas**

Python backend development.

---

This project is part of my hands-on journey toward becoming a Python backend developer.