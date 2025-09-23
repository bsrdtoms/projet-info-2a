# Diagramme d'état - Navigation utilisateur MagicSearch

```mermaid
stateDiagram-v2
    [*] --> Accueil
    Accueil: Écran d'accueil

    %% --- Connexion & Création ---
    Accueil --> Connexion: Se connecter
    Accueil --> CreationCompte: Créer un compte

    Connexion --> Accueil: Connexion réussie
    Connexion --> Accueil: Annuler

    CreationCompte --> Connexion: Compte créé → Connexion
    CreationCompte --> Accueil: Annuler

    %% --- Recherche ---
    Accueil --> Recherche: Rechercher une carte
    Recherche --> Resultats: Afficher résultats
    Resultats --> Recherche: Nouvelle recherche
    Resultats --> Favoris: Ajouter aux favoris
    Favoris --> Resultats: Retour résultats

    %% --- Historique ---
    Accueil --> Historique: Consulter historique
    Historique --> Accueil: Retour accueil

    %% --- Gestion de compte ---
    Accueil --> GestionCompte: Gérer compte
    GestionCompte --> Accueil: Retour accueil
    GestionCompte --> Deconnexion: Se déconnecter

    %% --- Fin ---
    Deconnexion --> [*]
