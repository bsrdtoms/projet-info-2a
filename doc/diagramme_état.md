# Diagramme d’état – Application MagicSearch (complet)

```mermaid
stateDiagram-v2
    [*] --> Accueil
    Accueil: Écran\nd'accueil

    %% --- Connexion & Création de compte ---
    Accueil --> Connexion: Se connecter
    Accueil --> CreationCompte: Créer un compte
    Connexion --> Accueil: Connexion réussie
    Connexion --> Accueil: Annuler
    CreationCompte --> Connexion: Compte créé\nSe connecter
    CreationCompte --> Accueil: Annuler

    %% --- Recherche & Favoris ---
    Accueil --> Recherche: Rechercher\nune carte
    Recherche --> Resultats: Afficher\nrésultats
    Resultats --> Recherche: Nouvelle\nrecherche
    Resultats --> Favoris: Ajouter aux\nfavoris
    Favoris --> Resultats: Retour\nrésultats
    Resultats --> Clusters: Explorer\nclusters
    Clusters --> Resultats: Retour\nrésultats

    %% --- Historique ---
    Accueil --> Historique: Consulter\nhistorique
    Historique --> Accueil: Retour accueil

    %% --- Gestion de compte utilisateur ---
    Accueil --> GestionCompte: Gérer\ncompte
    GestionCompte --> Accueil: Retour accueil
    GestionCompte --> Deconnexion: Se\ndéconnecter

    %% --- Administrateur ---
    Accueil --> Administrateur1: Accès admin 1
    Accueil --> Administrateur2: Accès admin 2

    Administrateur1 --> GestionCartes: Gérer\nles cartes
    GestionCartes --> AjouterCarte: Ajouter\nune carte
    GestionCartes --> ModifierCarte: Modifier\nune carte
    GestionCartes --> SupprimerCarte: Supprimer\nune carte
    AjouterCarte --> GestionCartes
    ModifierCarte --> GestionCartes
    SupprimerCarte --> GestionCartes
    GestionCartes --> Administrateur1

    Administrateur2 --> GestionUtilisateurs: Gérer\nles comptes
    GestionUtilisateurs --> AjouterCompte: Ajouter\nun compte
    GestionUtilisateurs --> ModifierCompte: Modifier\nun compte
    GestionUtilisateurs --> SupprimerCompte: Supprimer\nun compte
    AjouterCompte --> GestionUtilisateurs
    ModifierCompte --> GestionUtilisateurs
    SupprimerCompte --> GestionUtilisateurs
    GestionUtilisateurs --> Administrateur2

    Administrateur1 --> Accueil: Retour accueil
    Administrateur2 --> Accueil: Retour accueil

    %% --- Fin ---
    Deconnexion --> [*]
