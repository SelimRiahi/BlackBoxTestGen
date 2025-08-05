 Feature: User Registration and Authentication
     Scenario: Register a new user with valid credentials
       Given a new user wants to register
       When they provide a username (3-30 characters) and password (minimum 8 characters)
       And submit the registration form
       Then the backend should validate the provided information
       And store the credentials securely after hashing the password
       And return a JWT token

     Scenario: Failed user registration with invalid username or password length
       Given a new user wants to register with an invalid username or password length
       When they submit the registration form
       Then the frontend should display validation errors for the input fields

     Scenario: Login with valid credentials
       Given a registered user has their credentials
       When they enter the correct username and password
       And submit the login form
       Then the backend should validate the provided information
       And return a JWT token

     Scenario: Failed login with incorrect credentials
       Given an unregistered or incorrect user enters their credentials
       When they attempt to log in
       Then the frontend should display validation errors for the input fields

   Feature: Task Management
     Scenario: Create a new task
       Given a logged-in user on the dashboard
       When they provide task details and submit the form
       And the frontend validates the inputs
       Then the backend processes and stores the task ensuring ownership

     Scenario: View tasks
       Given a logged-in user on the dashboard
       Then the frontend should display their tasks from the /tasks endpoint

     Scenario: Edit a task
       Given a logged-in user with editable task on the dashboard
       When they click to edit the task
       And updates are sent via PATCH requests
       Then the backend should process the partial updates and save changes

     Scenario: Delete a task
       Given a logged-in user with deletable task on the dashboard
       When they confirm to delete the task
       Then a DELETE request is sent to the backend

     Scenario: Search tasks by title or keyword
       Given a logged-in user on the dashboard
       When they search for tasks using keywords
       Then the frontend sends queries to the /tasks/search endpoint
       And receives case-insensitive matches from the backend

   Feature: Category System
     Scenario: Create a new category
       Given a logged-in user on the dashboard
       When they provide a name and optionally color for a new category
       And submit the form to create the category
       Then the backend validates and stores the new category

     Scenario: Display categories in task forms and dashboard filters
       Given a logged-in user on the dashboard
       Then the frontend should pull categories from the /categories endpoint
       And display them as options in the task form and filterable options for the task list

   Feature: System Performance
     Scenario: Backend response time within 300ms
       Given a request to the backend
       When the request is processed
       Then the backend should respond within 300ms

     Scenario: Frontend rendering under 1 second
       Given a loaded page on the frontend
       When user actions trigger API calls or operations
       Then the frontend should render in under 1 second

   Feature: Real-Time UI Updates and Loading Indicators
     Scenario: UI updates via API polling/WebSockets during operations
       Given a user performing an action on the dashboard
       When the backend processes the request
       Then the frontend should update the UI in real-time using API polling or WebSockets

     Scenario: Loading indicators during API calls
       Given a user initiating an action on the dashboard triggering an API call
       When the call is being processed by the backend
       Then the frontend should display loading spinners indicating ongoing operations

