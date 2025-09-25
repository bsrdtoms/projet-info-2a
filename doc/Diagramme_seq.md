```mermaid
sequenceDiagram
    autonumber
    participant U as Utilisateur
    participant V as RechercheVue
    participant CS as CarteMagieService
    participant CD as CarteMagieDAO
    participant EM as EmbeddingModel
    participant DB as Base_de_donnees
    participant HS as HistoriqueService
    participant HD as HistoriqueDAO

    %% Étape 1: Initiation recherche sémantique
    U->>V: Saisit requête sémantique ("carte dragon volant")
    V->>CS: rechercheSemantique(requete_texte)

    %% Étape 2: Transformation sémantique
    rect rgba(200,200,255,0.1)
        CS->>EM: genererEmbedding(requete_texte)
        EM-->>CS: embedding_requete
    end

    %% Étape 3: Recherche par similarité
    rect rgba(200,255,200,0.1)
        CS->>CD: trouverCartesSimilaires(embedding_requete)
        CD->>DB: SELECT avec similarité_cosinus(embedding_carte, ?)
        DB-->>CD: cartes triées par score (0.95, 0.87, 0.76...)
        CD-->>CS: liste_cartes_ordonnee
    end

    %% Étape 4: Retour résultats
    CS-->>V: resultats_recherche

    %% Étape 5: Sauvegarde historique (conditionnel)
    alt Utilisateur connecté
        rect rgba(255,255,200,0.1)
            V->>HS: ajouterRecherche(utilisateur_id, requete, resultats)
            HS->>HD: creer(entree_historique)
            HD->>DB: INSERT INTO historique_recherche
            DB-->>HD: confirmation
            HD-->>HS: succes
            HS-->>V: historique_mis_a_jour
        end
    end

    %% Étape 6: Affichage final
    V->>U: Affiche cartes avec scores de similarité
