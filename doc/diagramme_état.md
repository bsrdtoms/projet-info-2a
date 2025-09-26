# State Diagram – MagicSearch Application (Improved Layout)

```mermaid
stateDiagram-v2
    %% --- Initial State ---
    [*] --> Home
    Home: Home\nscreen

    %% --- Login & Account Creation ---
    Home --> Login: Log in
    Home --> SignUp: Create\nan account

    Login --> Home: Login\nsuccessful
    Login --> Home: Cancel

    SignUp --> Login: Account\ncreated\n(Log in)
    SignUp --> Home: Cancel

    %% --- Search & Favorites ---
    Home --> Search: Search\nfor a card
    Search --> Results: Display\nresults

    Results --> Search: New\nsearch
    Results --> Favorites: Add to\nfavorites
    Favorites --> Results: Back to\nresults

    Results --> Clusters: Explore\nclusters
    Clusters --> Results: Back to\nresults

    %% --- History ---
    Home --> History: View\nhistory
    History --> Home: Back to\nhome

    %% --- Account Management ---
    Home --> AccountManagement: Manage\naccount
    AccountManagement --> Home: Back to\nhome
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
