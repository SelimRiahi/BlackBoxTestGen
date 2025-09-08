Feature: User Registration
  As a new user
  I want to register for an account
  So that I can manage my tasks

  Scenario: Register with valid credentials
    Given I am on the registration page
    When I enter a username with at least 3 characters
    And I enter a password with at least 8 characters
    And I click the register button
    Then I should see a confirmation message
    And I should receive authentication access

  Scenario: Register with username less than 3 characters
    Given I am on the registration page
    When I enter a username with less than 3 characters
    And I enter a password with at least 8 characters
    And I click the register button
    Then I should see a failure message
    And registration should fail


Feature: User Login
  As a registered user
  I want to log into my account
  So that I can access my tasks

  Scenario: Login with valid credentials
    Given I am on the login page
    And I have a registered account with valid username and password
    When I enter my correct username
    And I enter my correct password
    And I click the login button
    Then I should see a confirmation message
    And I should be redirected to the task creation form

  Scenario: Login with incorrect credentials
    Given I am on the login page
    When I enter an incorrect username or password
    And I click the login button
    Then I should see a failure message
    And login should fail


Feature: User Logout
  As a logged-in user
  I want to logout of my account
  So that my session is ended securely

  Scenario: Logout from authenticated session
    Given I am logged into the application
    When I click the logout button
    Then I should see a confirmation message
    And I should be redirected to the login page


Feature: Task Creation
  As a logged-in user
  I want to create a new task
  So that I can track my work

  Scenario: Create task with required title
    Given I am logged into the application
    And I am on the task creation form
    When I enter a task title
    And I optionally enter description, priority, category, and due date
    And I click the create task button
    Then I should see a confirmation message
    And the task should be created

  Scenario: Create task without required title
    Given I am logged into the application
    And I am on the task creation form
    When I leave the title field empty
    And I click the create task button
    Then I should see a failure message
    And task creation should fail


Feature: Task Completion
  As a logged-in user
  I want to mark a task as completed
  So that I can track my progress

  Scenario: Mark existing task as completed
    Given I am logged into the application
    And I have at least one pending task in my task list
    When I click the complete button for a specific task
    Then I should see a confirmation message
    And the task should be marked as completed


Feature: Task Deletion
  As a logged-in user
  I want to delete a task
  So that I can remove tasks I no longer need

  Scenario: Delete an existing task
    Given I am logged into the application
    And I have at least one task in my task list
    When I click the delete button for a specific task
    Then I should see a confirmation message
    And the task should be permanently deleted
