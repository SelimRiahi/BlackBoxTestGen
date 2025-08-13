Feature: Generic Application Test Scenarios
  As a user testing any web application
  I want to perform various user interactions
  So that I can verify the application responds correctly to both valid and invalid inputs

Scenario: Register
    Given I am on the registration page
    When I enter an empty string into the "Username" field
    When I enter an empty string into the "Password" field
    And I click the "Register" button
    Then I should see "Login/RegisterRegistration successful! Please login.LoginRegister"

Scenario: Register - Empty Fields Failure
  Given I am on the registration page
  When I enter "" into the "Username" field
  When I enter "" into the "Password" field
  And I click the "Register" button
  Then I should see an error message indicating that either the "Username" or "Password" fields are required or empty

Scenario: Register - Invalid Data Failure
    Given I am on the registration page
    When I enter an empty string into the "Username"
    When I enter "123" into the "Password"
    And I click the "Register"
    Then I should see an "invalid" or "format" error message

Scenario: Register - Incomplete Form Failure
  Given I am on the registration page
  When I enter an empty value into the "Username" field
  And I click the "Register" button
  Then I should see "required field" error message

Scenario: Login
    Given I am on the login page
    When I enter (empty) into the "Username"
    When I enter (empty) into the "Password"
    And I click the "Login"
    Then I should see "LogoutCreate TaskLowMediumHighSelect CategoryWorkHackedAdd TaskYour TasksNo tasks found"

Scenario: Login - Empty Fields Failure
  Given I am on the login page
  When I enter "" into the "Username" field
  When I enter "" into the "Password" field
  And I click the "Login" button
  Then I should see "required" or "empty" error message

Scenario: Login - Invalid Data Failure
  Given I am on the login page
  When I enter "" into the "Username"
  When I enter "" into the "Password"
  And I click the "Login"
  Then I should see "invalid" or "format" error message

Scenario: Login - Incomplete Form Failure
    Given I am on the login page
    When I enter an empty value into the "Username" field
    And I click the "Login" button
    Then I should see "required field" error message

Scenario: Add Task
  Given I am on the creation page
  When I enter an empty string into the "Username" field
  When I enter an empty string into the "Password" field
  And I click the "Login" button
  When I enter an empty string into the "Title" field
  When I enter an empty string into the "Description" field
  When I enter an empty string into the "select dropdown" field
  When I enter an empty string into the "Select Category" field
  When I enter an empty date into the "date input" field
  And I click the "Add Task" button
  Then I should see "Your TasksDeletetitleDescriptionPriority: mediumDue: an empty date formatCategory: Hacked"

Scenario: Add Task - Empty Fields Failure
  Given I am on the creation page
  When I enter an empty string into the "Username" field
  When I enter an empty string into the "Password" field
  And I click the "Login" button
  When I enter an empty string into the "Title" field
  When I enter an empty string into the "Description" field
  When I enter an empty string into the "select dropdown" field
  When I enter an empty string into the "Select Category" field
  When I enter an empty string into the date input field
  And I click the "Add Task" button
  Then I should see either a "required" or "empty" error message

Scenario: Add Task - Invalid Data Failure
    Given I am on the creation page
    When I enter an empty value into the "Username"
    When I enter "123" into the "Password"
    And I click the "Login"
    When I enter an empty value into the "Title"
    When I enter an empty value into the "Description"
    When I enter an empty value into the "select dropdown"
    When I enter an empty value into the "Select Category"
    When I enter "2025-13-45" into the "date input"
    And I click the "Add Task"
    Then I should see an "invalid" or "format" error message

Scenario: Add Task - Incomplete Form Failure
    Given I am on the creation page
    When I enter an empty value into the "Username"
    When I enter an empty value into the "Password"
    And I click the "Login"
    When I enter an empty value into the "Title"
    When I enter an empty value into the "Description"
    When I enter an empty value into the "select dropdown"
    When I enter an empty value into the "Select Category"
    And I click the "Add Task"
    Then I should see "required field" error message

Scenario: Delete
    Given I am on the management page
    When I enter "" into the "Username"
    When I enter "" into the "Password"
    And I click the "Login"
    And I click the "Delete"
    Then element with selector "#task-689a87dbd954eff4b5f50b01" should be removed

Scenario: Delete - Empty Fields Failure
  Given I am on the management page
  When I enter "" into the "Username"
  When I enter "" into the "Password"
  And I click the "Login"
  And I click the "Delete"
  Then element with selector "#task-689a87dbd954eff4b5f50b01" should still be visible

Scenario: Delete - Invalid Data Failure
  Given I am on the management page
  When I enter "" into the "Username"
  When I enter "123" into the "Password"
  And I click the "Login"
  And I click the "Delete"
  Then element with selector "#task-689a87dbd954eff4b5f50b01" should still be visible

Scenario: Delete - Incomplete Form Failure
  Given I am on the management page
  When I enter "" into the "Username"
  And I click the "Login"
  And I click the "Delete"
  Then element with selector "#task-689a87dbd954eff4b5f50b01" should still be visible

Scenario: Logout
    Given I am on the main page
    When I enter an empty string into the "Username" field
    When I enter an empty string into the "Password" field
    And I click the "Login" button
    And I click the "Logout" button
    Then I should see "Login/Register"

Scenario: Logout - Empty Fields Failure
    Given I am on the main page
    When I enter "" into the "Username"
    When I enter "" into the "Password"
    And I click the "Login"
    And I click the "Logout"
    Then I should see "required" or "empty" error message

Scenario: Logout - Invalid Data Failure
  Given I am on the main page
  When I enter an empty string into the "Username"
  When I enter "123" into the "Password"
  And I click the "Login"
  And I click the "Logout"
  Then I should see an "invalid" or "format" error message

Scenario: Logout - Incomplete Form Failure
  Given I am on the main page
  When I enter an empty string into the "Username"
  And I click the "Login"
  And I click the "Logout"
  Then I should see "required field" error message