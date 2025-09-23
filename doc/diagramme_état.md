# Diagramme d'état -  Point de vue utilisateur

```mermaid
stateDiagram-v2
    [*] --> Accueil
    Accueil: Écran d'accueil

    Accueil --> Connexion: cliquer sur se connecter
    Accueil --> CreationCompte: cliquer sur créer un compte
    Accueil --> Recherche: effectuer une recherche
    Accueil --> Historique: consulter l'historique
    Accueil --> GestionCompte: gérer son compte

    Connexion --> Accueil: connexion réussie
    Connexion --> Accueil: annuler

    CreationCompte --> Connexion: compte créé, se connecter
    CreationCompte --> Accueil: annuler

    Recherche --> Resultats: afficher les résultats
    Resultats --> Recherche: nouvelle recherche
    Resultats --> Favoris: ajouter une carte aux favoris

    Favoris --> Resultats: retour aux résultats

    Historique --> Accueil: retour accueil
    GestionCompte --> Accueil: retour accueil
    GestionCompte --> Deconnexion: cliquer sur déconnexion

    Deconnexion --> [*]
