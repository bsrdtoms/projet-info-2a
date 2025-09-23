# Diagramme d'état - Navigation utilisateur MagicSearch

```mermaid
stateDiagram-v2
    [*] --> Accueil
    Accueil: Écran\nd'accueil

    %% --- Connexion & Création ---
    Accueil --> Connexion: Se connecter
    Accueil --> CreationCompte: Créer un compte

    Connexion --> Accueil: Connexion réussie
    Connexion --> Accueil: Annuler

    CreationCompte --> Connexion: Compte créé\nSe connecter
    CreationCompte --> Accueil: Annuler

    
    %% --- Recherche ---
    Accueil --> Recherche: Rechercher\nune carte
    Recherche --> Resultats: Afficher\nrésultats
    Resultats --> Recherche: Nouvelle\nrecherche
    Resultats --> Favoris: Ajouter aux\nfavoris
    Favoris --> Resultats: Retour\nrésultats

    
    %% --- Historique ---
    Accueil --> Historique: Consulter\nhistorique
    Historique --> Accueil: Retour accueil

    
    %% --- Gestion de compte ---
    Accueil --> GestionCompte: Gérer\ncompte
    GestionCompte --> Accueil: Retour accueil
    GestionCompte --> Deconnexion: Se\ndéconnecter

    
    %% --- Fin ---
    Deconnexion --> [*]
