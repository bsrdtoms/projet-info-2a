```mermaid
classDiagram
    %% Entités principales
    class Utilisateur {
        +id_utilisateur: int
        +pseudo: string
        +email: string
        +mot_de_passe: string
        +role: string
        +date_creation: datetime
    }

    class CarteMagic {
        +id_carte: int
        +nom: string
        +description: string
        +type: string
        +couleur: string
        +rareté: string
        +date_creation: datetime
        +date_mise_a_jour: datetime
        +vector_embedding: list[float]
    }

    class Favoris {
        +id_utilisateur: int
        +id_carte: int
        +date_ajout: datetime
    }

    class HistoriqueRecherche {
        +id_recherche: int
        +id_utilisateur: int
        +requete: string
        +date_recherche: datetime
    }

    %% DAO
    class UtilisateurDao {
        +creer(Utilisateur): bool
        +trouver_par_id(int): Utilisateur
        +trouver_par_pseudo(str): Utilisateur
        +supprimer(Utilisateur): bool
        +lister_tous(): list[Utilisateur]
    }

    class CarteMagicDao {
        +creer(CarteMagic): bool
        +trouver_par_id(int): CarteMagic
        +lister_tous(): list[CarteMagic]
        +supprimer(CarteMagic): bool
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(vector: list[float], top_n: int): list[CarteMagic]
        +random(): CarteMagic
        +mettre_a_jour(CarteMagic): bool
    }

    class FavorisDao {
        +ajouter_favoris(int, int): bool
        +lister_favoris(int): list[CarteMagic]
        +supprimer_favoris(int, int): bool
    }

    class HistoriqueRechercheDao {
        +ajouter_recherche(int, str): bool
        +lister_historique(int): list[HistoriqueRecherche]
    }

    %% Services
    class UtilisateurService {
        +inscrire(str, str, str, str): Utilisateur
        +se_connecter(str, str): Utilisateur
        +supprimer_utilisateur(int): bool
    }

    class CarteMagicService {
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(str): list[CarteMagic]
        +random(): CarteMagic
        +ajouter_carte(dict): CarteMagic
        +supprimer_carte(int): bool
        +mettre_a_jour_carte(CarteMagic): bool
    }

    class FavorisService {
        +ajouter_favoris(int, int): bool
        +lister_favoris(int): list[CarteMagic]
        +supprimer_favoris(int, int): bool
    }

    %% Vues / API
    class VueAbstraite {
        <<abstract>>
        +afficher()
        +choisir_menu()
    }

    class AccueilVue {
        +afficher_accueil()
    }

    class RechercheVue {
        +afficher_resultats(list[CarteMagic])
        +effectuer_recherche(str)
    }

    class GestionCarteVue {
        +afficher_carte(CarteMagic)
        +ajouter_carte()
        +supprimer_carte(int)
        +mettre_a_jour_carte(CarteMagic)
    }

    %% Relations entre classes
    VueAbstraite <|-- AccueilVue
    VueAbstraite <|-- RechercheVue
    VueAbstraite <|-- GestionCarteVue

    RechercheVue ..> CarteMagicService : appelle
    GestionCarteVue ..> CarteMagicService : appelle
    GestionCarteVue ..> UtilisateurService : appelle

    CarteMagicService ..> CarteMagicDao : appelle
    CarteMagicService ..> HistoriqueRechercheDao : appelle
    FavorisService ..> FavorisDao : appelle
    UtilisateurService ..> UtilisateurDao : appelle

    Utilisateur <.. UtilisateurService : utilise
    Utilisateur <.. UtilisateurDao : utilise
    CarteMagic <.. CarteMagicService : utilise
    CarteMagic <.. CarteMagicDao : utilise
    Favoris <.. FavorisService : utilise
    Favoris <.. FavorisDao : utilise
    HistoriqueRecherche <.. HistoriqueRechercheDao : utilise
