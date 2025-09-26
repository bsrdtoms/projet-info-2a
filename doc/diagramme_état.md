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

    Results --> Search: New\nsearch
    Results --> Favorites: Add to favorites
    Favorites --> Results: Back to results

    Results --> Clusters: Explore clusters
    Clusters --> Results: Back to results

    %% --- History ---
    Home --> History: View history
    History --> Home: Back to home

    %% --- Account Management ---
    Home --> AccountManagement: Manage account
    AccountManagement --> Logout: Log\nout

    %% --- Administrator 1 (Card Management) ---
    Home --> Admin1: Access\nAdmin 1

    Admin1 --> CardManagement: Manage\ncards
    CardManagement --> AddCard: Add\na card
    CardManagement --> EditCard: Edit\na card
    CardManagement --> DeleteCard: Delete\na card

    AddCard --> CardManagement
    EditCard --> CardManagement
    DeleteCard --> CardManagement
    CardManagement --> Admin1

    Admin1 --> Home: Back to\nhome

    %% --- Administrator 2 (User Management) ---
    Home --> Admin2: Access\nAdmin 2

    Admin2 --> UserManagement: Manage\nuser\naccounts
    UserManagement --> AddAccount: Add\nan account
    UserManagement --> EditAccount: Edit\nan account
    UserManagement --> DeleteAccount: Delete\nan account

    AddAccount --> UserManagement
    EditAccount --> UserManagement
    DeleteAccount --> UserManagement
    UserManagement --> Admin2

    Admin2 --> Home: Back to\nhome

    %% --- End ---
    Logout --> [*]
