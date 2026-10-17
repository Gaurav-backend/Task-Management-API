from sqlalchemy import select
from app.models.task import Task

def test_root(client, setup_database):
    response = client.get("/")

    assert response.status_code == 200


def test_create_task(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "title": "Learn pytest",
            "description": "Write my first database test",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Learn pytest"
    assert data["description"] == "Write my first database test"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_get_tasks(client, setup_database):
    # Create a task first
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Learn GET requests",
            "description": "Practice testing GET endpoints",
        },
    )

    assert create_response.status_code == 201

    # Get all tasks
    response = client.get("/tasks/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Learn GET requests"
    assert data[0]["description"] == "Practice testing GET endpoints"
    assert data[0]["completed"] is False

def test_get_task(client, setup_database):
    # Create a task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Learn FastAPI testing",
            "description": "Practice GET by ID",
        },
    )

    assert create_response.status_code == 201

    created_task = create_response.json()
    task_id = created_task["id"]

    # Get the task by ID
    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Learn FastAPI testing"
    assert data["description"] == "Practice GET by ID"
    assert data["completed"] is False


def test_get_task_not_found(client, setup_database):
    response = client.get("/tasks/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(client, setup_database):
    # Create a task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original title",
            "description": "Original description",
        },
    )

    assert create_response.status_code == 201

    created_task = create_response.json()
    task_id = created_task["id"]

    # Update only the completed field
    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "completed": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Original title"
    assert data["description"] == "Original description"
    assert data["completed"] is True

def test_update_task_not_found(client, setup_database):
    response = client.patch(
        "/tasks/9999",
        json={
            "completed": True,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task(client, setup_database):
    # Create a task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Task to delete",
            "description": "This task should be deleted",
        },
    )

    assert create_response.status_code == 201

    created_task = create_response.json()
    task_id = created_task["id"]

    # Delete the task
    delete_response = client.delete(
        f"/tasks/{task_id}"
    )

    assert delete_response.status_code == 204

    # Verify the task no longer exists
    get_response = client.get(
        f"/tasks/{task_id}"
    )

    assert get_response.status_code == 404

def test_delete_task_not_found(client, setup_database):
    response = client.delete("/tasks/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_create_task_missing_title(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "description": "This request has no title",
        },
    )

    assert response.status_code == 422

def test_create_task_invalid_title_type(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "title": 12345,
        },
    )

    assert response.status_code == 422


def test_create_task_empty_title(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "title": "",
        },
    )

    assert response.status_code == 422

def test_create_task_whitespace_only_title(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "title": "     ",
        },
    )

    assert response.status_code == 422


def test_create_task_whitespace_only_description(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "title": "Learn FastAPI",
            "description": "     ",
        },
    )

    assert response.status_code == 422


def test_update_task_empty_title(client, setup_database):
    # Create a valid task first
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original title",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    # Try to update with an empty title
    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "",
        },
    )

    assert response.status_code == 422


def test_update_task_whitespace_title(client, setup_database):
    # Create a valid task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original title",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    # Try to update with whitespace-only title
    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "     ",
        },
    )

    assert response.status_code == 422


def test_update_task_whitespace_description(client, setup_database):
    # Create a valid task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original title",
            "description": "Original description",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    # Try to update with whitespace-only description
    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "description": "     ",
        },
    )

    assert response.status_code == 422


def test_update_task_invalid_completed_type(client, setup_database):
    # Create a valid task
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Test completed validation",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    # Try to update completed with an invalid type
    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "completed": "yes",
        },
    )

    assert response.status_code == 422

def test_create_task_invalid_description_type(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "title": "Learn FastAPI",
            "description": 12345,
        },
    )

    assert response.status_code == 422


def test_create_task_invalid_title_boolean(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "title": True,
        },
    )

    assert response.status_code == 422

def test_create_task_invalid_description_boolean(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "title": "Learn FastAPI",
            "description": True,
        },
    )

    assert response.status_code == 422


def test_update_task_invalid_description_type(client, setup_database):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original task",
            "description": "Original description",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "description": 12345,
        },
    )

    assert response.status_code == 422


def test_update_task_invalid_completed_integer(client, setup_database):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Test completed validation",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "completed": 1,
        },
    )

    assert response.status_code == 422

def test_update_task_only_title(client, setup_database):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original title",
            "description": "Original description",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated title"
    assert data["description"] == "Original description"
    assert data["completed"] is False


def test_update_task_only_description(client, setup_database):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original title",
            "description": "Original description",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "description": "Updated description",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Original title"
    assert data["description"] == "Updated description"
    assert data["completed"] is False

def test_update_task_only_completed(client, setup_database):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original title",
            "description": "Original description",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "completed": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Original title"
    assert data["description"] == "Original description"
    assert data["completed"] is True


def test_update_task_all_fields(client, setup_database):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original title",
            "description": "Original description",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
            "description": "Updated description",
            "completed": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated title"
    assert data["description"] == "Updated description"
    assert data["completed"] is True

def test_delete_task_does_not_delete_other_tasks(client, setup_database):
    first_response = client.post(
        "/tasks/",
        json={
            "title": "Task A",
            "description": "This task will be deleted",
        },
    )

    second_response = client.post(
        "/tasks/",
        json={
            "title": "Task B",
            "description": "This task should remain",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_task_id = first_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{first_task_id}"
    )

    assert delete_response.status_code == 204

    response = client.get("/tasks/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Task B"
    assert data[0]["description"] == "This task should remain"

def test_get_multiple_tasks(client, setup_database):
    response_a = client.post(
        "/tasks/",
        json={"title": "Task A"},
    )

    response_b = client.post(
        "/tasks/",
        json={"title": "Task B"},
    )

    response_c = client.post(
        "/tasks/",
        json={"title": "Task C"},
    )

    assert response_a.status_code == 201
    assert response_b.status_code == 201
    assert response_c.status_code == 201

    response = client.get("/tasks/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data[0]["title"] == "Task A"
    assert data[1]["title"] == "Task B"
    assert data[2]["title"] == "Task C"

def test_get_tasks_after_deleting_one(client, setup_database):
    response_a = client.post(
        "/tasks/",
        json={"title": "Task A"},
    )

    response_b = client.post(
        "/tasks/",
        json={"title": "Task B"},
    )

    response_c = client.post(
        "/tasks/",
        json={"title": "Task C"},
    )

    assert response_a.status_code == 201
    assert response_b.status_code == 201
    assert response_c.status_code == 201

    task_b_id = response_b.json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_b_id}"
    )

    assert delete_response.status_code == 204

    response = client.get("/tasks/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "Task A"
    assert data[1]["title"] == "Task C"


def test_health_check(client, setup_database):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task_is_saved_in_database(
    client,
    db_session,
    setup_database,
):
    response = client.post(
        "/tasks/",
        json={
            "title": "Database test",
            "description": "Verify task is saved",
        },
    )

    assert response.status_code == 201

    task_id = response.json()["id"]

    task = db_session.scalar(
        select(Task).where(Task.id == task_id)
    )

    assert task is not None
    assert task.title == "Database test"
    assert task.description == "Verify task is saved"
    assert task.completed is False

def test_delete_task_removes_from_database(
    client,
    db_session,
    setup_database,
):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Delete database test",
            "description": "This should be removed",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/tasks/{task_id}"
    )

    assert delete_response.status_code == 204

    task = db_session.scalar(
        select(Task).where(Task.id == task_id)
    )

    assert task is None


def test_update_task_changes_database(
    client,
    db_session,
    setup_database,
):
    create_response = client.post(
        "/tasks/",
        json={
            "title": "Original title",
            "description": "Original description",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "Updated title",
            "description": "Updated description",
            "completed": True,
        },
    )

    assert update_response.status_code == 200

    task = db_session.scalar(
        select(Task).where(Task.id == task_id)
    )

    assert task is not None
    assert task.title == "Updated title"
    assert task.description == "Updated description"
    assert task.completed is True


def test_create_task_is_committed(
    client,
    second_db_session

):
    response = client.post(
        "/tasks/",
        json={
            "title": "Commit test",
            "description": "Check transaction commit",
        },
    )

    assert response.status_code == 201

    task_id = response.json()["id"]

    task = second_db_session.scalar(
        select(Task).where(Task.id == task_id)
    )

    assert task is not None
    assert task.title == "Commit test"


def test_database_isolation_first(client, setup_database):
    response = client.post(
        "/tasks/",
        json={
            "title": "Task from first test",
        },
    )

    assert response.status_code == 201

    response = client.get("/tasks/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_database_isolation_second(client, setup_database):
    response = client.get("/tasks/")

    assert response.status_code == 200
    assert response.json() == []


from sqlalchemy.exc import SQLAlchemyError


def test_health_ready_database_unavailable(
    client,
    db_session,
    monkeypatch,
):
    def fail_execute(*args, **kwargs):
        raise SQLAlchemyError("Simulated database failure")

    monkeypatch.setattr(db_session, "execute", fail_execute)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database unavailable"
    }