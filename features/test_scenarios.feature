Feature: User Registration

  Scenario: Successful registration with valid credentials
    Given the user is on the registration page
    When the user fills in the registration form and submits it
    Then a success message is displayed
    And the user receives a JWT token

  Scenario: Failed registration with invalid username
    Given the user is on the registration page
    When the user fills in the registration form with an invalid username and submits it
    Then an error message indicating an invalid username is displayed
    And no JWT token is received

  Scenario: Failed registration with weak password
    Given the user is on the registration page
    When the user fills in the registration form with a weak password and submits it
    Then an error message indicating a weak password is displayed
    And no JWT token is received

Feature: Task Management

  Scenario: Successful task creation with valid inputs
    Given the user is logged in and on the dashboard page
    When the user fills in the task form with valid inputs and submits it
    Then the new task appears in the task list
    And a success notification is displayed

  Scenario: Failed task creation with invalid title
    Given the user is logged in and on the dashboard page
    When the user fills in the task form with an invalid title and submits it
    Then an error message indicating an invalid title is displayed
    And no new task appears in the task list

Feature: Category Management

  Scenario: Successful category creation with valid inputs
    Given the user is logged in and on the dashboard page
    When the user fills in the category form with valid inputs and submits it
    Then the new category appears in the category management panel
    And a success notification is displayed

  Scenario: Failed category creation with invalid name
    Given the user is logged in and on the dashboard page
    When the user fills in the category form with an invalid name and submits it
    Then an error message indicating an invalid name is displayed
    And no new category appears in the category management panel