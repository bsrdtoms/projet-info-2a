```mermaid
classDiagram
    %% ====================
    %% VUES 
    %% ====================
    class VueAbstraite {
        +afficher()
        +choisir_menu()
    }

    class AccueilVue
    class UtilisateurVue
    class RechercheVue

    VueAbstraite <|-- AccueilVue
    VueAbstraite <|-- UtilisateurVue
    VueAbstraite <|-- RechercheVue
    

    %% ====================
    %% UTILISATEURS
    %% ====================
    class UtilisateurService {
        %% tous %%
        +connexion(pseudo : str, mdp : str)
        +deconnexion()

        %% admin1 %%
        +creer_compte(pseudo, mdp)
        +supprimer_compte()
        +trouver_par_id(int): Utilisateur
        +lister_tous(): list[Utilisateur]
        
        %% client %%
        +ajouter_favori(CarteMagic)
        +supprimer_favori(CarteMagic)
        +historique_recherche()
    }

    class UtilisateurDao {
        +creer(Utilisateur)
        +supprimer(Utilisateur)

        %% modifier un utilisateur %%
        +ajouter_favori(Client, CarteMagic)
        +supprimer_favori(Client, CarteMagic)

        %% lire les données d'un utilisateur %%
        +historique_recherche(Client) : list[HistoriqueRecherche]
        +trouver_par_id(int): Utilisateur
        +lister_tous(): list[Utilisateur]
    }

    class Utilisateur {
        <<abstract>>
        +id_utilisateur: int
        +pseudo: string
        +mdp: string
    }

    class Admin1 
    class Admin2 
    class Client 

    UtilisateurVue ..> UtilisateurService : utilise

    UtilisateurService ..> UtilisateurDao : utilise

    UtilisateurDao ..> Utilisateur : manipule

    UtilisateurService ..> Utilisateur : manipule

    Utilisateur <|-- Admin1
    Utilisateur <|-- Admin2
    Utilisateur <|-- Client


    %% ====================
    %% CARTES
    %% ====================
    class CarteMagicService {
        +ajouter_carte(nom: str, text: str, type, couleur)
        +modifier_carte()
        +supprimer_carte(carte: CarteMagic)
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(str, model : EmbeddingModel): list[CarteMagic]
        +random(): CarteMagic
    }

    class CarteMagicDao {
        +creer(CarteMagic)
        +supprimer(CarteMagic)

        %% modifier %%
        +modifier()
        +ajouter_embedding(CarteMagic, list[float], type_de_modele : EmbeddingModel )

        %% lire %%
        +trouver_par_id(int): CarteMagic
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(list[float]): list[CarteMagic]
        +random(): CarteMagic
    }

    class CarteMagic {
        +id_carte: int
        +nom: str
        +text: str
        +type
        +couleur
        +vector_embedding: list[float]
        +short_description(): str
        +detailed_description(): str
    }

    RechercheVue ..> CarteMagicService : utilise

    CarteMagicService ..> CarteMagicDao : utilise

    CarteMagicDao ..> CarteMagic : manipule

    CarteMagicService ..> CarteMagic : utilise

    %% Embedding %%
    class EmbeddingModel {
        +generer_embedding(str): list[float]
    }

    class Model1 {
        +generer_embedding(str): list[float]
    }

    class Model2 {
        +generer_embedding(str): list[float]
    }

    class Model3 {
        +generer_embedding(str): list[float]
    }

    EmbeddingModel <|-- Model1
    EmbeddingModel <|-- Model2
    EmbeddingModel <|-- Model3

    CarteMagicService ..> EmbeddingModel : utilise

    %% performance %%
    class PerformanceEvaluator {
        +jeu_test: dict
        +precision_at_k(int): float
        +recall_at_k(int): float
        +f1_score(int): float
        +evaluer_modele(EmbeddingModel): dict
    }

    PerformanceEvaluator ..> EmbeddingModel : évalue
    PerformanceEvaluator ..> CarteMagicService : utilise




    %% ====================
    %% HISTORIQUE
    %% ====================
    class HistoriqueService {
        +ajouter_recherche(Client, requete: str, resultats: list[CarteMagic])
        +consulter(Client): list[HistoriqueRecherche]
    }

    class HistoriqueDao {
        +ajouter(Client, HistoriqueRecherche)
        +lire_historique(Client): list[HistoriqueRecherche]
    }

    class HistoriqueRecherche {
        +id_historique: int
        +requete: string
        +date: datetime
        +resultats: list[CarteMagic]
    }

    RechercheVue ..> HistoriqueService : utilise

    HistoriqueService ..> HistoriqueDao : utilise

    HistoriqueService ..> HistoriqueRecherche : manipule

    HistoriqueDao ..> HistoriqueRecherche : manipule


    %% ====================
    %% CLUSTERING
    %% ====================
    class ClusteringService {
        +entrainer(list[CarteMagic], modele: EmbeddingModel, algo: ClusteringModel)
        +obtenir_clusters(): dict[int, list[CarteMagic]]
        +trouver_cluster(CarteMagic): int
    }

    class ClusteringModel {
        +entrainer(list[list[float]])
        +predire(list[float]) : int
    }

    class ModelClust1
    class ModelClust2

    RechercheVue ..> ClusteringService : use
    ClusteringService ..> CarteMagicDao : utilise
    ClusteringService ..> ClusteringModel : utilise algo

    ClusteringModel <|.. ModelClust1
    ClusteringModel <|.. ModelClust2


    %% ====================
    %% AUTRES RELATIONS
    %% ====================
    UtilisateurVue ..> CarteMagicService : utilise
    Client "1" --> "*" HistoriqueRecherche : possède
    Client "*" -- "*" CarteMagic : possède
    


