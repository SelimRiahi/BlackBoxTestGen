import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:3000"

def test_register():
    # Happy path
    data = {"username": "testuserfazfz", "password": "test12345678"}
    response = requests.post(f"{BASE_URL}/register", json=data)
    assert response.status_code == 201, "Failed to register user"

    # Error case: invalid username length
    data["username"] = "a" * 31
    response = requests.post(f"{BASE_URL}/register", json=data)
    assert response.status_code == 400, "Did not receive validation error for invalid username length"

def test_login():
    # Register user first
    register_response = requests.post(f"{BASE_URL}/register", json={"username": "testuser", "password": "test12345678"})
    assert register_response.status_code == 201, "Failed to register user"

    # Happy path
    login_data = {"username": "testuser", "password": "test12345678"}
    login_response = requests.post(f"{BASE_URL}/login", json=login_data)
    assert login_response.status_code == 200, "Failed to log in user"

    # Error case: invalid credentials
    login_data["password"] = "wrongPassword"
    login_response = requests.post(f"{BASE_URL}/login", json=login_data)
    assert login_response.status_code == 401, "Did not receive unauthorized error for invalid credentials"

def test_create_task():
    # Login first
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "test12345678"})
    token = login_response.json()["token"]

    # Happy path
    task_data = {"title": "Test Task"}
    response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json=task_data)
    assert response.status_code == 201, "Failed to create task"

def test_get_tasks():
    # Login first and create tasks
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "test12345678"})
    token = login_response.json()["token"]

    # Create some tasks
    create_task_1_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Task 1"})
    create_task_2_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Task 2"})

    # Happy path: get user's tasks
    response = requests.get(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "Failed to get user's tasks"
    assert len(response.json()) == 2, "Incorrect number of tasks returned"

def test_get_task():
    # Login first and create a task
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "test12345678"})
    token = login_response.json()["token"]

    # Create a task
    create_task_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test Task"})
    task_id = create_task_response.json()["_id"]

    # Happy path: get the task
    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "Failed to get task"

def test_update_task():
    # Login first and create a task
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "test12345678"})
    token = login_response.json()["token"]

    # Create a task
    create_task_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test Task"})
    task_id = create_task_response.json()["_id"]

    # Happy path: update the task
    updated_data = {"title": "Updated Test Task"}
    response = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"}, json=updated_data)
    assert response.status_code == 200, "Failed to update task"

def test_delete_task():
    # Login first and create a task
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "test12345678"})
    token = login_response.json()["token"]

    # Create a task
    create_task_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test Task"})
    task_id = create_task_response.json()["_id"]

    # Happy path: delete the task
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204, "Failed to delete task"