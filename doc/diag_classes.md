```mermaid
classDiagram
    %% Entité principale
    class CarteMagic {
        +id_carte: int
        +nom: string
        +description: string
        +type: string
        +couleur: string
        +vector_embedding: list[float]
    }

    %% DAO
    class CarteMagicDao {
        +creer(CarteMagic): bool
        +trouver_par_id(int): CarteMagic
        +lister_tous(): list[CarteMagic]
        +supprimer(CarteMagic): bool
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(vector: list[float], top_n: int): list[CarteMagic]
        +random(): CarteMagic
    }

    %% Service
    class CarteMagicService {
        +rechercher_par_nom(str): list[CarteMagic]
        +rechercher_semantique(str): list[CarteMagic]
        +random(): CarteMagic
    }

    %% Vues / API
    class VueAbstraite {
        +afficher()
        +choisir_menu()
    }

    class AccueilVue
    class RechercheVue

    %% Relations
    VueAbstraite <|-- AccueilVue
    VueAbstraite <|-- RechercheVue

    RechercheVue ..> CarteMagicService : appelle
    CarteMagicService ..> CarteMagicDao : appelle
    CarteMagic <.. CarteMagicService : utilise
    CarteMagic <.. CarteMagicDao : utilise
