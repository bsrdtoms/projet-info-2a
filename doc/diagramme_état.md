# State Diagram – MagicSearch Application (Improved Layout)

```mermaid
stateDiagram-v2
    %% --- Initial State ---
    [*] --> Home
    Home: Home screen

    %% --- Login & Account Creation ---
    Home --> Login: Log in
    Home --> SignUp: Create an account

    Login --> Home: Login successful
    Login --> Home: Cancel

    SignUp --> Login: Account created (Log in)
    SignUp --> Home: Cancel

    %% --- Search & Favorites ---
    Home --> Search: Search for a card
    Search --> Results: Display results

    Results --> Search: New search
    Results --> Favorites: Add to favorites
    Favorites --> Results: Back to results

    Results --> Clusters: Explore clusters
    Clusters --> Results: Back to results

    %% --- History ---
    Home --> History: View history
    

    %% --- Account Management ---
    Home --> AccountManagement: Manage account
    AccountManagement --> Logout: Log out

    %% --- Administrator 1 (Card Management) ---
    Home --> Admin1: Access Admin 1

    Admin1 --> CardManagement: Manage cards
    CardManagement --> AddCard: Add a card
    CardManagement --> EditCard: Edit a card
    CardManagement --> DeleteCard: Delete a card

    AddCard --> CardManagement
    EditCard --> CardManagement
    DeleteCard --> CardManagement
    CardManagement --> Admin1

    Admin1 --> Home: Back to home

    %% --- Administrator 2 (User Management) ---
    Home --> Admin2: Access Admin 2

    Admin2 --> UserManagement: Manage user accounts
    UserManagement --> AddAccount: Add an account
    UserManagement --> EditAccount: Edit an account
    UserManagement --> DeleteAccount: Delete an account

    AddAccount --> UserManagement
    EditAccount --> UserManagement
    DeleteAccount --> UserManagement
    UserManagement --> Admin2

    

    %% --- End ---
    Logout --> [*]
