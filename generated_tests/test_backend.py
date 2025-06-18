import pytest
import json
from datetime import datetime, timedelta
import requests

BASE_URL = "http://localhost:3000"

# Test Authentication - POST /register
def test_register():
    data = {"username": "ihebnjili", "password": "test12345678"}
    response = requests.post(f"{BASE_URL}/register", json=data)
    assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
    assert "token" in response.json(), "Response should contain a 'token'"

def test_register_invalid_username():
    data = {"username": "a", "password": "test12345678"}
    response = requests.post(f"{BASE_URL}/register", json=data)
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

def test_register_invalid_password():
    data = {"username": "testuser", "password": "123"}
    response = requests.post(f"{BASE_URL}/register", json=data)
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"

# Test Authentication - POST /login
def test_login():
    # Register a user first
    register_response = requests.post(f"{BASE_URL}/register", json={"username": "testuser2", "password": "test12345678"})
    assert register_response.status_code == 201, f"Expected status code 201 for registration, got {register_response.status_code}"

    login_data = {"username": "testuser2", "password": "test12345678"}
    login_response = requests.post(f"{BASE_URL}/login", json=login_data)
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"
    assert "token" in login_response.json(), "Response should contain a 'token'"

def test_login_invalid_credentials():
    login_data = {"username": "testuser", "password": "test12345678"}
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    assert response.status_code == 401, f"Expected status code 401 for invalid credentials, got {response.status_code}"

# Test Tasks - POST /tasks
def test_create_task():
    # Login first
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    data = {"title": "Test Task", "description": "This is a test task.", "priority": "medium"}
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=data)
    assert response.status_code == 201, f"Expected status code 201 for creating a task, got {response.status_code}"
    assert "title" in response.json(), "Response should contain 'title'"

def test_create_task_invalid_data():
    # Login first
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    data = {"title": "", "description": "This is a test task.", "priority": "medium"}
    response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=data)
    assert response.status_code == 400, f"Expected status code 400 for invalid data, got {response.status_code}"

# Test Tasks - GET /tasks
def test_get_tasks():
    # Login first and create tasks
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create tasks
    create_task1_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json={"title": "Task 1", "description": "Description 1"})
    create_task2_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json={"title": "Task 2", "description": "Description 2"})

    get_tasks_response = requests.get(f"{BASE_URL}/tasks", headers=headers)
    assert get_tasks_response.status_code == 200, f"Expected status code 200 for getting tasks, got {get_tasks_response.status_code}"
    assert len(get_tasks_response.json()) == 2, "Expected 2 tasks in the response"

# Test Tasks - GET /tasks/:id
def test_get_task():
    # Login first and create a task
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_task_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json={"title": "Test Task", "description": "This is a test task."})
    assert create_task_response.status_code == 201, f"Expected status code 201 for creating a task, got {create_task_response.status_code}"

    get_task_response = requests.get(f"{BASE_URL}/tasks/{create_task_response.json()['_id']}", headers=headers)
    assert get_task_response.status_code == 200, f"Expected status code 200 for getting a task, got {get_task_response.status_code}"
    assert "title" in get_task_response.json(), "Response should contain 'title'"

def test_get_non_existent_task():
    # Login first
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    get_non_existent_task_response = requests.get(f"{BASE_URL}/tasks/invalid_id", headers=headers)
    assert get_non_existent_task_response.status_code == 404, f"Expected status code 404 for non-existent task, got {get_non_existent_task_response.status_code}"

# Test Tasks - PATCH /tasks/:id
def test_update_task():
    # Login first and create a task
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_task_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json={"title": "Test Task", "description": "This is a test task."})
    assert create_task_response.status_code == 201, f"Expected status code 201 for creating a task, got {create_task_response.status_code}"

    update_task_data = {"title": "Updated Test Task"}
    update_task_response = requests.patch(f"{BASE_URL}/tasks/{create_task_response.json()['_id']}", headers=headers, json=update_task_data)
    assert update_task_response.status_code == 200, f"Expected status code 200 for updating a task, got {update_task_response.status_code}"
    assert "title" in update_task_response.json(), "Response should contain 'title'"
    assert update_task_response.json()["title"] == "Updated Test Task", f"Expected updated title to be 'Updated Test Task', got {update_task_response.json()['title']}"

def test_update_non_existent_task():
    # Login first
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_non_existent_task_response = requests.patch(f"{BASE_URL}/tasks/invalid_id", headers=headers, json={"title": "Updated Test Task"})
    assert update_non_existent_task_response.status_code == 404, f"Expected status code 404 for non-existent task, got {update_non_existent_task_response.status_code}"

# Test Tasks - DELETE /tasks/:id
def test_delete_task():
    # Login first and create a task
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_task_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json={"title": "Test Task", "description": "This is a test task."})
    assert create_task_response.status_code == 201, f"Expected status code 201 for creating a task, got {create_task_response.status_code}"

    delete_task_response = requests.delete(f"{BASE_URL}/tasks/{create_task_response.json()['_id']}", headers=headers)
    assert delete_task_response.status_code == 204, f"Expected status code 204 for deleting a task, got {delete_task_response.status_code}"

def test_delete_non_existent_task():
    # Login first
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    delete_non_existent_task_response = requests.delete(f"{BASE_URL}/tasks/invalid_id", headers=headers)
    assert delete_non_existent_task_response.status_code == 404, f"Expected status code 404 for non-existent task, got {delete_non_existent_task_response.status_code}"

# Test Tasks - GET /tasks/search?q=query
def test_search_tasks():
    # Login first and create tasks with matching search query
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_task1_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json={"title": "Test Task 1", "description": "This is a test task with query in the title."})
    create_task2_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json={"title": "Test Task 2", "description": "This is another test task."})

    search_query = "test"
    search_response = requests.get(f"{BASE_URL}/tasks/search?q={search_query}", headers=headers)
    assert search_response.status_code == 200, f"Expected status code 200 for searching tasks, got {search_response.status_code}"
    assert len(search_response.json()) == 1, "Expected 1 task in the response"
    assert search_response.json()[0]["title"] == "Test Task 1", f"Expected first task to be 'Test Task 1', got {search_response.json()[0]['title']}"

def test_search_tasks_case_insensitive():
    # Login first and create tasks with matching search query (case-insensitive)
    login_response = requests.post(f"{BASE_URL}/login", json={"username": "testuser2", "password": "test12345678"})
    assert login_response.status_code == 200, f"Expected status code 200 for login, got {login_response.status_code}"

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_task1_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json={"title": "Test Task 1", "description": "This is a test task with query in the title."})
    create_task2_response = requests.post(f"{BASE_URL}/tasks", headers=headers, json={"title": "Test Task 2", "description": "This is another test task."})

    search_query = "test"
    search_response = requests.get(f"{BASE_URL}/tasks/search?q={search_query.lower()}", headers=headers)
    assert search_response.status_code == 200, f"Expected status code 200 for searching tasks, got {search_response.status_code}"
    assert len(search_response.json()) == 1, "Expected 1 task in the response"
    assert search_response.json()[0]["title"] == "Test Task 1", f"Expected first task to be 'Test Task 1', got {search_response.json()[0]['title']}"