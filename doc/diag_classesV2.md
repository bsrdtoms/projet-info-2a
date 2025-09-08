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
        +creer_compte()
        +supprimer_compte()
        +connexion()
        +deconnexion()
        +ajouter_favori(Client, CarteMagic)
        +supprimer_favori(Client, CarteMagic)
        +historique_recherche()
        +trouver_par_id(int): Utilisateur
        +lister_tous(): list[Utilisateur]
    }

    class UtilisateurDao {
        +creer_compte()
        +supprimer_compte()
        +connexion()
        +deconnexion()
        +ajouter_favori(Client, CarteMagic)
        +supprimer_favori(Client, CarteMagic)
        +historique_recherche()
        +trouver_par_id(int): Utilisateur
        +lister_tous(): list[Utilisateur]
    }

    class Utilisateur {
        <<abstract>>
        +id_utilisateur: int
        +pseudo: string
        +mdp: string
        +type
    }

    class Admin1 
    class Admin2 
    class Client 

    UtilisateurVue ..> UtilisateurService : use

    UtilisateurService ..> UtilisateurDao : use

    Utilisateur <.. UtilisateurService : create

    Utilisateur <|-- Admin1
    Utilisateur <|-- Admin2
    Utilisateur <|-- Client


    %% ====================
    %% CARTES
    %% ====================
    class CarteMagicService {
        +ajouter_carte(carte: CarteMagic)
        +modifier_carte()
        +supprimer_carte(carte: CarteMagic)
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(str, filtres: ?, exclusions: ?): list[CarteMagic]
        +random(): CarteMagic
    }

    class CarteMagicDao {
        +creer(CarteMagic): bool
        +trouver_par_id(int): CarteMagic
        +supprimer(CarteMagic): bool
        +modifier(CarteMagic): bool
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(): list[CarteMagic]
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

    RechercheVue ..> CarteMagicService : use

    CarteMagicService ..> CarteMagicDao : use

    CarteMagic <.. CarteMagicService


    %% ====================
    %% HISTORIQUE
    %% ====================
    class HistoriqueService {
        +ajouter_recherche(Client, requete: str, resultats: list[CarteMagic])
        +consulter(Client): list[HistoriqueRecherche]
    }

    class HistoriqueDao {
        +ajouter(Client, HistoriqueRecherche)
        +lister_par_client(Client): list[HistoriqueRecherche]
    }

    class HistoriqueRecherche {
        +id_historique: int
        +requete: string
        +date: datetime
        +resultats: list[CarteMagic]
    }

    RechercheVue ..> HistoriqueService : use

    HistoriqueService ..> HistoriqueDao : use

    HistoriqueRecherche <.. HistoriqueService


    %% ====================
    %% AUTRES RELATIONS
    %% ====================
    UtilisateurVue ..> CarteMagicService : use
    Client "1" --> "*" HistoriqueRecherche : possède
    


