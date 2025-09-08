```mermaid
classDiagram
    %% ====================
    %% UTILISATEURS
    %% ====================
    class Utilisateur {
        <<abstract>>
        +id_utilisateur: int
        +pseudo: string
        +mdp: string
    }

    class Admin1 {
        +consulter_donnees_clients()
    }

    class Admin2 {
        +ajouter_carte(CarteMagic)
        +supprimer_carte(CarteMagic)
        +modifier_carte(CarteMagic)
    }

    class Client {
        #favoris: list[CarteMagic]
        #historique_recherche: list[HistoriqueRecherche]
    }

    Utilisateur <|-- Admin1
    Utilisateur <|-- Admin2
    Utilisateur <|-- Client

    %% ====================
    %% CARTES & HISTORIQUE
    %% ====================
    class CarteMagic {
        +id_carte: int
        +nom: string
        +description: string
        +type: string
        +couleur: string
        +vector_embedding: list[float]
        +short_description(): str
        +detailed_description(): str
    }

    class HistoriqueRecherche {
        +id_historique: int
        +requete: string
        +resultats: list[CarteMagic]
        +date: datetime
    }

    HistoriqueRecherche "*" --> "*" CarteMagic : résultats
    Cluster "*" --> "*" CarteMagic : regroupe

    %% ====================
    %% DAO
    %% ====================
    class UtilisateurDao {
        +creer(Utilisateur): bool
        +trouver_par_id(int): Utilisateur
        +lister_tous(): list[Utilisateur]
        +supprimer(Utilisateur): bool
        +se_connecter(str,str): Utilisateur
        +ajouter_favori(Client, CarteMagic)
        +supprimer_favori(Client, CarteMagic)
    }

    class CarteMagicDao {
        +creer(CarteMagic): bool
        +trouver_par_id(int): CarteMagic
        +lister_tous(): list[CarteMagic]
        +supprimer(CarteMagic): bool
        +modifier(CarteMagic): bool
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(vector: list[float], filtres: ?, exclusions: ?): list[CarteMagic]
        +random(): CarteMagic
    }

    %% ====================
    %% SERVICES
    %% ====================
    class UtilisateurService {
        +creer(str...): Utilisateur
        +se_connecter(str,str): Utilisateur
        +ajouter_favori(Client, CarteMagic)
        +supprimer_favori(Client, CarteMagic)
        +historique_recherche(Client, str, list[CarteMagic])
    }

    class CarteMagicService {
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(str, filtres: ?, exclusions: ?): list[CarteMagic]
        +random(): CarteMagic
    }

    class EmbeddingModel {
        +nom: string
        +generer_embedding(str): list[float]
    }

    class PerformanceEvaluator {
        +jeu_test: dict
        +precision_at_k(int): float
        +recall_at_k(int): float
        +f1_score(int): float
        +evaluer_modele(EmbeddingModel): dict
    }

    class ClusteringService {
        +generer_clusters(list[CarteMagic]): list[Cluster]
        +visualiser_clusters(list[Cluster])
    }

    class Cluster {
        +id_cluster: int
        +cartes: list[CarteMagic]
    }

    %% ====================
    %% RELATIONS SERVICE <-> DAO
    %% ====================
    UtilisateurService ..> UtilisateurDao
    CarteMagicService ..> CarteMagicDao
    CarteMagicService ..> EmbeddingModel
    PerformanceEvaluator ..> CarteMagicService
    PerformanceEvaluator ..> EmbeddingModel
    ClusteringService --> Cluster

    CarteMagic <.. CarteMagicDao : utilise
    CarteMagic <.. CarteMagicService : utilise
    Utilisateur <.. UtilisateurDao : utilise
    Utilisateur <.. UtilisateurService : utilise

    %% ====================
    %% VUES / API
    %% ====================
    class VueAbstraite {
        +afficher()
        +choisir_menu()
    }

    class AccueilVue
    class ConnexionVue
    class MenuUtilisateurVue
    class RechercheVue
    class WebVue

    VueAbstraite <|-- AccueilVue
    VueAbstraite <|-- ConnexionVue
    VueAbstraite <|-- MenuUtilisateurVue
    VueAbstraite <|-- RechercheVue
    VueAbstraite <|-- WebVue

    MenuUtilisateurVue ..> UtilisateurService
    RechercheVue ..> CarteMagicService
    WebVue ..> CarteMagicService
