# Black-Box Gherkin Test Scenarios - Task Management System

Feature: User Registration

  Scenario: Successful user registration
    Given I am on the registration page
    When I enter a username with 3 or more characters
    And I enter a password with 8 or more characters
    And I click the register button
    Then I should see a confirmation message
    And I should be provided with access to the system

  Scenario: Registration fails with short username
    Given I am on the registration page
    When I enter a username with less than 3 characters
    And I enter a password with 8 or more characters
    And I click the register button
    Then I should see a failure message
    And registration should not be completed

Feature: User Login

  Scenario: Successful user login
    Given I am a registered user
    And I am on the login page
    When I enter my correct username
    And I enter my correct password
    And I click the login button
    Then I should see a confirmation message
    And I should be redirected to the task creation form

  Scenario: Login fails with incorrect credentials
    Given I am on the login page
    When I enter an incorrect username or password
    And I click the login button
    Then I should see a failure message
    And I should remain on the login page

Feature: User Logout

  Scenario: Successful user logout
    Given I am logged into the system
    When I perform the logout action
    Then I should see a confirmation message
    And I should be redirected to the login page

Feature: Task Creation

  Scenario: Successful task creation with required fields
    Given I am logged into the system
    And I am on the task creation form
    When I enter a title for the task
    And I optionally enter description, priority, category, and due date
    And I submit the task form
    Then I should see a confirmation message
    And the task should be created

  Scenario: Task creation fails without title
    Given I am logged into the system
    And I am on the task creation form
    When I leave the title field empty
    And I submit the task form
    Then I should see a failure message
    And the task should not be created

Feature: Task Completion

  Scenario: Successfully mark task as completed
    Given I am logged into the system
    And I have at least one pending task in my task list
    When I select the option to mark the task as completed
    Then I should see a confirmation message
    And the task should be marked as completed

Feature: Task Deletion

  Scenario: Successfully delete a task
    Given I am logged into the system
    And I have at least one task in my task list
    When I select the option to delete the task
    Then I should see a confirmation message
    And the task should be permanently removed from my task list

Feature: Task Viewing

  Scenario: View task collection
    Given I am logged into the system
    When I navigate to view my tasks
    Then I should see my complete task collection
    And completed tasks should be visually distinguished
    And overdue tasks should be flagged
