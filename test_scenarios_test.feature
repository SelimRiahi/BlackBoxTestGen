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