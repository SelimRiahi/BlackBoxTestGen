Feature: User Authentication
     Scenario: Register a new user
       Given there is no authenticated user
       When the user navigates to registration page
       And provides a valid username and password
       Then the system should return a success message
       And store the user's credentials securely
       And generate a JWT token
    