 Feature: User Authentication
     Scenario: Register a new user
       Given there is no authenticated user
       When the user navigates to registration page
       And provides a valid username and password
       Then the system should return a success message
       And store the user's credentials securely
       And generate a JWT token
     Scenario: Log in an existing user
       Given there is a registered user with valid credentials
       When the user navigates to login page
       And enters their username and password
       Then the system should verify the credentials
       And return a JWT token if valid
       And redirect the user to the dashboard
     Scenario: Unauthorized API request
       Given a user who is not authenticated
       When they make an API request
       Then the server should return an unauthorized error

   Feature: Task Management
     Scenario: Create a new task
       Given a logged-in user
       When the user navigates to task creation page
       And fills out the task form with required fields
       Then the system should validate the inputs
       And store the task in the database
     Scenario: View tasks
       Given a logged-in user
       When the user navigates to the dashboard or tasks page
       Then the system should display the user's tasks
     Scenario: Edit a task
       Given a logged-in user and an existing task
       When the user navigates to edit the task
       And updates the task with valid changes
       Then the system should update the task in the database
     Scenario: Delete a task
       Given a logged-in user and an existing task
       When the user initiates deletion of the task
       And confirms the action in a dialog box
       Then the system should delete the task from the database
     Scenario: Search tasks
       Given a logged-in user with multiple tasks
       When the user searches for tasks by title, description, priority, or category
       Then the system should return case-insensitive matches

   Feature: Category System
     Scenario: Create a new category
       Given a logged-in user
       When the user navigates to create a new category page
       And provides a name and color (optional) for the category
       Then the system should validate the inputs
       And store the category in the database
     Scenario: Display categories
       Given a logged-in user with created categories
       When the user navigates to the dashboard or tasks page
       Then the system should display the created categories

   Feature: System Performance
     Scenario: Fast backend response time
       Given any API request from the frontend
       When the server processes the request
       Then the response should be returned within 300ms

     Scenario: Fast frontend rendering
       Given a user who navigates to a page
       When the frontend loads the data from the backend
       Then the page should render in under 1 second

   Feature: Real-time UI updates
     Scenario: Update UI in real-time
       Given a user interacting with the application
       When any changes are made to the server
       Then the frontend should update the UI accordingly via API polling or WebSockets

   Feature: Security & Compatibility
     Scenario: Protect against XSS/CSRF
       Given a user who navigates to the application
       When they make any requests or interact with forms
       Then the system should protect against Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF) attacks

     Scenario: Enforce ownership checks
       Given a user who wants to perform an action on another user's task/category
       When they attempt to do so without proper authorization
       Then the system should return an error or deny the request

     Scenario: Support modern browsers and devices
       Given any user accessing the application
       When they use popular modern browsers (Chrome, Firefox, Safari) or various devices (mobile/desktop)
       Then the system should function properly without compatibility issues

