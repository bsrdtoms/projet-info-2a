# Diagramme d'état - Navigation utilisateur MagicSearch

```mermaid
stateDiagram-v2
    [*] --> "Écran d'accueil"

    "Écran d'accueil" --> "Connexion": cliquer sur se connecter
    "Écran d'accueil" --> "Création de compte": cliquer sur créer un compte
    "Écran d'accueil" --> "Recherche de cartes": effectuer une recherche
    "Écran d'accueil" --> "Historique": consulter l'historique
    "Écran d'accueil" --> "Gestion de compte": gérer son compte

    "Connexion" --> "Écran d'accueil": connexion réussie
    "Connexion" --> "Écran d'accueil": annuler

    "Création de compte" --> "Connexion": compte créé, se connecter
    "Création de compte" --> "Écran d'accueil": annuler

    "Recherche de cartes" --> "Navigation des résultats": afficher les résultats
    "Navigation des résultats" --> "Recherche de cartes": nouvelle recherche
    "Navigation des résultats" --> "Ajout aux favoris": ajouter une carte

    "Ajout aux favoris" --> "Navigation des résultats": retour aux résultats

    "Historique" --> "Écran d'accueil": retour accueil
    "Gestion de compte" --> "Écran d'accueil": retour accueil
    "Gestion de compte" --> "Déconnexion": cliquer sur déconnexion

    "Déconnexion" --> [*]
