Feature: User flows recorded on 09/08/2025 6:57:10 PM

Scenario: Register
  Given I am on the page "http://localhost:3001"
  When I enter "kih" into the "Username"
  When I enter "kih" into the "Password"
  And I click the "Username"
  And I click the "Password"
  And I click the "Register"
  Then I should see "Login/RegisterRegistration successful! Please login.LoginRegister"

Scenario: Login
  Given I am on the page "http://localhost:3001"
  When I enter "kih" into the "Username"
  When I enter "kih" into the "Password"
  And I click the "Username"
  And I click the "html"
  And I click the "Password"
  And I click the "Login"
  Then I should see "LogoutCreate TaskLowMediumHighSelect CategoryWorkHackedAdd TaskYour TasksNo tasks found"

Scenario: Add Task
  Given I am on the page "http://localhost:3001"
  When I enter "kih" into the "Username"
  When I enter "kih" into the "Password"
  And I click the "Username"
  And I click the "html"
  And I click the "Password"
  And I click the "Login"
  When I enter "azezae" into the "Title"
  When I enter "testozaa" into the "Description"
  When I enter "medium" into the "select dropdown"
  When I enter "<hidden value>" into the "Select Category"
  When I enter "2026-06-06" into the "date input"
  And I click the "Title"
  And I click the "Description"
  And I click the "select dropdown"
  And I click the "Select Category"
  And I click the "date input"
  And I click the "Add Task"
  Then I should see "Your TasksDeleteazezaetestozaaPriority: mediumDue: 06/06/2026Category: Hacked"

Scenario: Delete
  Given I am on the page "http://localhost:3001"
  When I enter "kih" into the "Username"
  When I enter "kih" into the "Password"
  And I click the "Username"
  And I click the "html"
  And I click the "Password"
  And I click the "Login"
  And I click the "Delete"
  Then element with selector "#task-68978bb4036ce5784330053a" should be removed

Scenario: Logout
  Given I am on the page "http://localhost:3001"
  When I enter "kih" into the "Username"
  When I enter "kih" into the "Password"
  And I click the "Username"
  And I click the "html"
  And I click the "Password"
  And I click the "Login"
  And I click the "Logout"
  Then I should see "Login/RegisterLoginRegister"

