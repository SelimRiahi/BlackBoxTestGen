import pytest
import requests

BASE_URL = "http://localhost:3000"

def test_create_task():
    response = requests.post(f"{BASE_URL}/tasks", json={"title": "Test Task"})
    assert response.status_code == 201, "Expected status code 201 but got {}".format(response.status_code)
    assert "_id" in response.json(), "Response should contain an 'id' field"
    assert "title" in response.json(), "Response should contain a 'title' field"

def test_create_task_invalid_input():
    response = requests.post(f"{BASE_URL}/tasks", json={"title": 123})
    assert response.status_code == 400, "Expected status code 400 but got {}".format(response.status_code)

def test_get_all_tasks():
    # Assuming that create_task() has been called previously to populate the database with tasks
    response = requests.get(f"{BASE_URL}/tasks")
    assert response.status_code == 200, "Expected status code 200 but got {}".format(response.status_code)
    assert len(response.json()) > 0, "Response should contain at least one task"

def test_task_performance():
    # Testing performance by making requests and measuring the time taken
    import time

    start = time.time()
    _ = requests.post(f"{BASE_URL}/tasks", json={"title": "Performance Test"})
    end = time.time()
    assert end - start < 0.3, "Response time should be less than 300ms but was {}".format(end - start)

def test_database_persistence():
    # This test assumes that the API has been restarted after creating a task
    # If the task still exists after restart, then data persists
    response = requests.get(f"{BASE_URL}/tasks")
    assert len(response.json()) > 0, "Task should still exist in the database after restart"