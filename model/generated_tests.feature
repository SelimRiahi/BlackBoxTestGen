 Feature: User Registration

Scenario: Successful Registration
  Given I navigate to the registration page
  When I provide a unique username and a valid password with at least 8 characters
  Then I should be able to submit the form and receive a success message, without any errors

Scenario: Invalid Username Length
  Given I navigate to the registration page
  When I provide a password and a username shorter  than 3 characters
  Then I should see an error message prompting for a longer username

Feature: Login

Scenario: Successful Login
  Given I navigate to the login page
  When I provide my username and password on the login form
  Then I should be able to log in, receive a success message, and automatically load my tasks

Scenario: Invalid Credentials or Nonexistent User
  Given I try to log in with incorrect credentials or as a nonexistent user
  When I submit the login form
  Then I should see an error message and not be able to access the task management page

Feature: Logout

Scenario: Successful Logout
  Given I am logged in
  When I click on the logout button
  Then I should be redirected to the login view, with all data cleared from the UI

Feature: Task Creation

Scenario: Valid Task Creation
  Given I am logged in and navigate to the task creation page
  When I fill out a valid title, provide optional description, select priority, category, and due date in the future
  Then my new task should be created and added to my task list

Scenario: Missing Title or Invalid Due Date
  Given I am logged in and attempt to create a task
  When I submit the form without providing a title or with an invalid due date
  Then I should see an error message and not be able to create the task

Feature: Task Listing

Scenario: Viewing Tasks
  Given I am logged in
  When I navigate to my task list page
  Then I should see all of my tasks displayed as cards, with completion checkboxes and delete buttons

Scenario: Overdue Task Indicator
  Given I have an overdue task
  When I view the task list
  Then I should see a red indicator next to the overdue task

Feature: Marking Task as Complete

Scenario: Successfully Completing a Task
  Given I have a task in my task list
  When I check the completion checkbox for that task
  Then the task status should be updated, and it should appear with a green background in the task list

Feature: Deleting a Task

Scenario: Confirming and Deleting a Task
  Given I have a task in my task list
  When I click on the delete button for that task
  Then I should see a confirmation prompt asking if I want to delete the task, and upon confirming, the task should be permanently deleted from the list

Scenario: Failed Deletion Attempt (Task Not Found or Unauthorized)
  Given I attempt to delete a non-existent task or while not being authorized to perform the action
  When I click on the delete button for that task
  Then I should see an error message and the task should remain in the task list

