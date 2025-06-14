import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:3000"

def test_register():
    # Happy path
    data = {"username": "testuser", "password": "testpassword"}
    response = requests.post(f"{BASE_URL}/register", json=data)
    assert response.status_code == 201, "Expected status code 201"

    # Error case: invalid username length
    data["username"] = "a" * 31
    response = requests.post(f"{BASE_URL}/register", json=data)
    assert response.status_code == 400, "Expected status code 400"

def test_login():
    # Register a user first
    register_response = requests.post(f"{BASE_URL}/register", json={"username": "testuser", "password": "testpassword"})
    assert register_response.status_code == 201, "Expected status code 201 in registration"

    # Happy path
    login_data = {"username": "testuser", "password": "testpassword"}
    login_response = requests.post(f"{BASE_URL}/login", json=login_data)
    assert login_response.status_code == 200, "Expected status code 200 in login"
    token = login_response.json()["token"]

def test_create_task():
    # Login first
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200, "Expected status code 200 in login"
    token = login_response.json()["token"]

    # Happy path
    task_data = {"title": "Test Task", "description": "This is a test task."}
    response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json=task_data)
    assert response.status_code == 201, "Expected status code 201 in creating a task"

def test_get_tasks():
    # Login first and create tasks
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200, "Expected status code 200 in login"
    token = login_response.json()["token"]

    create_task1_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Task 1"})
    create_task2_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Task 2"})

    # Happy path
    response = requests.get(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "Expected status code 200 in getting tasks"
    tasks = response.json()
    assert len(tasks) == 2, "Expected to get both created tasks"

def test_get_task():
    # Login first and create a task
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200, "Expected status code 200 in login"
    token = login_response.json()["token"]

    create_task_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test Task"})
    task_id = create_task_response.json()["_id"]

    # Happy path
    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, "Expected status code 200 in getting a task"

def test_update_task():
    # Login first and create a task
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200, "Expected status code 200 in login"
    token = login_response.json()["token"]

    create_task_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test Task"})
    task_id = create_task_response.json()["_id"]

    # Happy path
    updated_data = {"title": "Updated Test Task"}
    response = requests.patch(f"{BASE_URL}/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"}, json=updated_data)
    assert response.status_code == 200, "Expected status code 200 in updating a task"

def test_delete_task():
    # Login first and create a task
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200, "Expected status code 200 in login"
    token = login_response.json()["token"]

    create_task_response = requests.post(f"{BASE_URL}/tasks", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test Task"})
    task_id = create_task_response.json()["_id"]

    # Happy path
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204, "Expected status code 204 in deleting a task"