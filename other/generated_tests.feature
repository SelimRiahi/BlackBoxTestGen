 # Feature: User Registration
   Scenario: Successful user registration
     Given the application is in the INITIAL_LOAD state
     When a user provides valid credentials and attempts to register via the "register" UI element
     Then the system should transition to the NAVIGATION state and store the new resource data

   Scenario: User registration with invalid credentials
     Given the application is in the INITIAL_LOAD state
     When a user provides invalid credentials and attempts to register via the "register" UI element
     Then the system should display an error message and remain in the INITIAL_LOAD state

   # Feature: User Authentication
   Scenario: Successful user authentication
     Given the application is in the NAVIGATION state with valid credentials stored for a resource
     When the user authenticates via the "login" UI element using those credentials
     Then the system should transition to the NAVIGATION state and allow access to protected resources

   Scenario: Failed user authentication with incorrect credentials
     Given the application is in the NAVIGATION state with invalid credentials stored for a resource
     When the user authenticates via the "login" UI element using those credentials
     Then the system should display an error message and remain in the NAVIGATION state

   # Feature: CRUD Operations
   Scenario: Successful creation of a new resource
     Given the application is in the NAVIGATION state with authenticated user credentials
     When the user adds a new resource via the appropriate UI element for that action (e.g., "add" UI element)
     Then the system should transition to the PATCH state, update the resource data, and then transition back to the NAVIGATION state

   Scenario: Failed creation of a new resource due to invalid data
     Given the application is in the NAVIGATION state with authenticated user credentials
     When the user attempts to add an invalid or incomplete resource via the appropriate UI element for that action (e.g., "add" UI element)
     Then the system should display an error message and remain in the NAVIGATION state

   Scenario: Successful retrieval of a specific resource by ID
     Given the application is in the NAVIGATION state with authenticated user credentials
     When the user selects a resource via the appropriate UI element for that action (e.g., "task-{{ID}}" UI element)
     Then the system should transition to the PATCH or GET state, display the selected resource details, and then transition back to the NAVIGATION state

   Scenario: Failed retrieval of a specific resource by ID due to invalid data
     Given the application is in the NAVIGATION state with authenticated user credentials
     When the user attempts to select an invalid or non-existent resource via the appropriate UI element for that action (e.g., "task-{{ID}}" UI element)
     Then the system should display an error message and remain in the NAVIGATION state

   Scenario: Successful modification of a specific resource by ID
     Given the application is in the PATCH or GET state with authenticated user credentials for a selected resource
     When the user modifies the selected resource data via the appropriate UI element for that action (e.g., "task" UI element)
     Then the system should update the resource data and transition back to the NAVIGATION state

   Scenario: Failed modification of a specific resource by ID due to invalid data
     Given the application is in the PATCH or GET state with authenticated user credentials for a selected resource
     When the user attempts to modify the selected resource with invalid or incomplete data via the appropriate UI element for that action (e.g., "task" UI element)
     Then the system should display an error message and remain in the PATCH or GET state

   Scenario: Successful deletion of a specific resource by ID
     Given the application is in the NAVIGATION state with authenticated user credentials
     When the user selects a resource for deletion via the appropriate UI element for that action (e.g., "delete-{{ID}}" UI element)
     Then the system should transition to the DELETE state, delete the selected resource data, and then transition back to the NAVIGATION state

   Scenario: Failed deletion of a specific resource by ID due to invalid data
     Given the application is in the NAVIGATION state with authenticated user credentials
     When the user attempts to delete an invalid or non-existent resource via the appropriate UI element for that action (e.g., "delete-{{ID}}" UI element)
     Then the system should display an error message and remain in the NAVIGATION state

   Scenario: Successful user logout
     Given the application is in the NAVIGATION state with authenticated user credentials
     When the user selects the "logout" UI element
     Then the system should transition to the INITIAL_LOAD state and remove the stored user credentials

