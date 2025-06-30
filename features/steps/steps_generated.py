from behave import given, when, then
import requests
import json

@given("the user is on the login page")
def step_impl_the_user_is_on_the_login_page(context):
    pass


@when("the user fills in the registration form and submits it")
def step_impl_the_user_fills_in_the_registration_form_and_submits_it(context):
    response = requests.post('http://localhost:3001/register', json={"username": "example_user", "email": "example@example.com", "password": "strong_password"})
    context.response = response

@then("a success message is displayed and a JWT token is received")
def step_impl_a_success_message_is_displayed_and_a_jwt_token_is_received(context):
    response = context.response
    assert response.status_code == 201, f'Expected status code 201 but got {response.status_code}'
    assert response.json().get('token') == "{{JWT_TOKEN}}", 'Expected token to be "{{JWT_TOKEN}}"'
    assert response.json().get('message') == "Registration successful", 'Expected message to be "Registration successful"'


@when("the user fills in the registration form with an invalid username and submits it")
def step_impl_the_user_fills_in_the_registration_form_with_an_invalid_username_and_submits_it(context):
    response = requests.post('http://localhost:3001/register', json={"username": "!@#$%^&*()", "email": "example@example.com", "password": "strong_password"})
    context.response = response

@then("an error message indicating an invalid username is displayed and no JWT token is received")
def step_impl_an_error_message_indicating_an_invalid_username_is_displayed_and_no_jwt_token_is_received(context):
    response = context.response
    assert response.status_code == 400, f'Expected status code 400 but got {response.status_code}'
    assert response.json().get('error') == "Invalid username", 'Expected error to be "Invalid username"'
    assert response.json().get('message') == "Registration failed", 'Expected message to be "Registration failed"'


@when("the user fills in the registration form with a weak password and submits it")
def step_impl_the_user_fills_in_the_registration_form_with_a_weak_password_and_submits_it(context):
    response = requests.post('http://localhost:3001/register', json={"username": "example_user", "email": "example@example.com", "password": "weak_password"})
    context.response = response

@then("an error message indicating a weak password is displayed and no JWT token is received")
def step_impl_an_error_message_indicating_a_weak_password_is_displayed_and_no_jwt_token_is_received(context):
    response = context.response
    assert response.status_code == 400, f'Expected status code 400 but got {response.status_code}'
    assert response.json().get('error') == "Weak password", 'Expected error to be "Weak password"'
    assert response.json().get('message') == "Registration failed", 'Expected message to be "Registration failed"'


@given("the user is logged in and on the dashboard page")
def step_impl_the_user_is_logged_in_and_on_the_dashboard_page(context):
    pass


@when("the user fills in the task form with valid inputs and submits it")
def step_impl_the_user_fills_in_the_task_form_with_valid_inputs_and_submits_it(context):
    response = requests.post('http://localhost:3001/tasks', json={"title": "example_task", "description": "example_description"})
    context.response = response

@then("the new task appears in the task list and a success notification is displayed")
def step_impl_the_new_task_appears_in_the_task_list_and_a_success_notification_is_displayed(context):
    response = context.response
    assert response.status_code == 201, f'Expected status code 201 but got {response.status_code}'
    assert response.json().get('task_id') == "{{TASK_ID}}", 'Expected task_id to be "{{TASK_ID}}"'
    assert response.json().get('message') == "Task created successfully", 'Expected message to be "Task created successfully"'


@when("the user fills in the task form with an invalid title and submits it")
def step_impl_the_user_fills_in_the_task_form_with_an_invalid_title_and_submits_it(context):
    response = requests.post('http://localhost:3001/tasks', json={"title": "!@#$%^&*()", "description": "example_description"})
    context.response = response

@then("an error message indicating an invalid title is displayed and no new task appears in the task list")
def step_impl_an_error_message_indicating_an_invalid_title_is_displayed_and_no_new_task_appears_in_the_task_list(context):
    response = context.response
    assert response.status_code == 400, f'Expected status code 400 but got {response.status_code}'
    assert response.json().get('error') == "Invalid title", 'Expected error to be "Invalid title"'
    assert response.json().get('message') == "Task creation failed", 'Expected message to be "Task creation failed"'


@when("the user fills in the category form with valid inputs and submits it")
def step_impl_the_user_fills_in_the_category_form_with_valid_inputs_and_submits_it(context):
    response = requests.post('http://localhost:3001/categories', json={"name": "example_category", "description": "example_description"})
    context.response = response

@then("the new category appears in the category management panel and a success notification is displayed")
def step_impl_the_new_category_appears_in_the_category_management_panel_and_a_success_notification_is_displayed(context):
    response = context.response
    assert response.status_code == 201, f'Expected status code 201 but got {response.status_code}'
    assert response.json().get('category_id') == "{{CATEGORY_ID}}", 'Expected category_id to be "{{CATEGORY_ID}}"'
    assert response.json().get('message') == "Category created successfully", 'Expected message to be "Category created successfully"'


@when("the user fills in the category form with an invalid name and submits it")
def step_impl_the_user_fills_in_the_category_form_with_an_invalid_name_and_submits_it(context):
    response = requests.post('http://localhost:3001/categories', json={"name": "!@#$%^&*()", "description": "example_description"})
    context.response = response

@then("an error message indicating an invalid name is displayed and no new category appears in the category management panel")
def step_impl_an_error_message_indicating_an_invalid_name_is_displayed_and_no_new_category_appears_in_the_category_management_panel(context):
    response = context.response
    assert response.status_code == 400, f'Expected status code 400 but got {response.status_code}'
    assert response.json().get('error') == "Invalid name", 'Expected error to be "Invalid name"'
    assert response.json().get('message') == "Category creation failed", 'Expected message to be "Category creation failed"'


@given("the user is on the registration page")
def step_impl_the_user_is_on_the_registration_page(context):
    pass


@when("the user submits the form with a username containing special characters and submits it")
def step_impl_the_user_submits_the_form_with_a_username_containing_special_characters_and_submits_it(context):
    response = requests.post('http://localhost:3001/register', json={"username": "!@#$%^&*()", "email": "example@example.com", "password": "strong_password"})
    context.response = response

@then("an error message indicating invalid username is displayed and no JWT token is received")
def step_impl_an_error_message_indicating_invalid_username_is_displayed_and_no_jwt_token_is_received(context):
    response = context.response
    assert response.status_code == 400, f'Expected status code 400 but got {response.status_code}'
    assert response.json().get('error') == "Invalid username", 'Expected error to be "Invalid username"'
    assert response.json().get('message') == "Registration failed", 'Expected message to be "Registration failed"'


@when("the user submits the form with an email containing special characters and submits it")
def step_impl_the_user_submits_the_form_with_an_email_containing_special_characters_and_submits_it(context):
    response = requests.post('http://localhost:3001/register', json={"username": "example_user", "email": "!@#$%^&*()@example.com", "password": "strong_password"})
    context.response = response

@then("an error message indicating invalid email is displayed and no JWT token is received")
def step_impl_an_error_message_indicating_invalid_email_is_displayed_and_no_jwt_token_is_received(context):
    response = context.response
    assert response.status_code == 400, f'Expected status code 400 but got {response.status_code}'
    assert response.json().get('error') == "Invalid email", 'Expected error to be "Invalid email"'
    assert response.json().get('message') == "Registration failed", 'Expected message to be "Registration failed"'


@when("the user submits the form with a weak password and submits it")
def step_impl_the_user_submits_the_form_with_a_weak_password_and_submits_it(context):
    response = requests.post('http://localhost:3001/register', json={"username": "example_user", "email": "example@example.com", "password": "weak_password"})
    context.response = response

@when("the user submits the form with a password containing special characters and submits it")
def step_impl_the_user_submits_the_form_with_a_password_containing_special_characters_and_submits_it(context):
    response = requests.post('http://localhost:3001/register', json={"username": "example_user", "email": "example@example.com", "password": "!@#$%^&*()"})
    context.response = response

@then("an error message indicating a password containing special characters is displayed and no JWT token is received")
def step_impl_an_error_message_indicating_a_password_containing_special_characters_is_displayed_and_no_jwt_token_is_received(context):
    response = context.response
    assert response.status_code == 400, f'Expected status code 400 but got {response.status_code}'
    assert response.json().get('error') == "Password with special characters not allowed", 'Expected error to be "Password with special characters not allowed"'
    assert response.json().get('message') == "Registration failed", 'Expected message to be "Registration failed"'

