DROP SCHEMA IF EXISTS project CASCADE;
CREATE SCHEMA project;

--------------------------------------------------------------
-- Types d Attaques
--------------------------------------------------------------

DROP TABLE IF EXISTS project.cards CASCADE ;
/*CREATE TABLE project.cards (
    id SERIAL PRIMARY KEY,
    name TEXT,
    type TEXT,
    mana_cost TEXT,
    mana_value FLOAT,
    layout TEXT,
    text TEXT,
    colors JSONB,
    color_identity JSONB,
    first_printing TEXT,
    printings JSONB,
    is_funny BOOLEAN,
    power TEXT,
    toughness TEXT,
    loyalty TEXT,
    identifiers JSONB,
    purchase_urls JSONB,
    foreign_data JSONB,
    legalities JSONB,
    rulings JSONB,
    embedding_of_text JSONB
);*

CREATE TABLE project.cards (
    id SERIAL PRIMARY KEY,          -- identifiant auto-incrémenté
    name TEXT NOT NULL,             -- nom de la carte
    type TEXT,                      -- type de la carte
    mana_cost TEXT,                 -- coût en mana
    mana_value FLOAT,               -- valeur numérique du mana
    layout TEXT,                    -- layout de la carte
    text TEXT,                      -- texte de la carte
    colors TEXT[],                  -- tableau des couleurs (ex: {G,R})
    color_identity TEXT[],          -- tableau des identités de couleurs
    first_printing TEXT,            -- première édition
    printings TEXT[],               -- éditions de la carte
    is_funny BOOLEAN,               -- carte humoristique
    power TEXT,                     -- force (nullable)
    toughness TEXT,                 -- endurance (nullable)
    loyalty TEXT,                   -- fidélité (nullable)
    identifiers JSONB,              -- identifiants (stockés en JSON)
    purchase_urls JSONB,            -- URLs d'achat (JSON)
    foreign_data JSONB,             -- données étrangères (JSON)
    legalities JSONB,               -- légalité (JSON)
    rulings JSONB,                  -- règles (JSON)
    embedding_of_text FLOAT[]       -- vecteur d'embedding (tableau de flottants)
);
*/

CREATE TABLE project.cards (
    id SERIAL PRIMARY KEY,                -- auto increment ID
    name TEXT NOT NULL,                   -- card name
    ascii_name TEXT,                      -- asciiName
    type TEXT,                            -- type (string form)
    types TEXT[],                         -- list of types
    subtypes TEXT[],                      -- list of subtypes
    supertypes TEXT[],                    -- list of supertypes
    mana_cost TEXT,                       -- manaCost
    mana_value FLOAT,                     -- manaValue
    converted_mana_cost FLOAT,            -- convertedManaCost (legacy alias)
    layout TEXT,                          -- layout
    text TEXT,                            -- card text
    colors TEXT[],                        -- colors
    color_identity TEXT[],                -- colorIdentity
    color_indicator TEXT[],               -- colorIndicator
    first_printing TEXT,                  -- firstPrinting
    printings TEXT[],                     -- printings
    is_funny BOOLEAN,                     -- isFunny
    is_game_changer BOOLEAN,              -- isGameChanger
    is_reserved BOOLEAN,                  -- isReserved
    keywords TEXT[],                      -- keywords
    power TEXT,                           -- power
    toughness TEXT,                       -- toughness
    defense TEXT,                         -- defense
    loyalty TEXT,                         -- loyalty
    hand TEXT,                            -- hand size modification
    life TEXT,                            -- life modification
    side TEXT,                            -- side (A/B)
    subsets TEXT[],                       -- subsets
    attraction_lights INT[],              -- attractionLights
    face_converted_mana_cost FLOAT,       -- faceConvertedManaCost
    face_mana_value FLOAT,                -- faceManaValue
    face_name TEXT,                       -- faceName
    edhrec_rank INT,                      -- edhrecRank
    edhrec_saltiness FLOAT,               -- edhrecSaltiness
    has_alternative_deck_limit BOOLEAN,   -- hasAlternativeDeckLimit
    identifiers JSONB,                    -- identifiers
    purchase_urls JSONB,                  -- purchaseUrls
    foreign_data JSONB,                   -- foreignData
    legalities JSONB,                     -- legalities
    rulings JSONB,                        -- rulings
    related_cards JSONB,                  -- relatedCards
    leadership_skills JSONB,              -- leadershipSkills
    embedding_of_text FLOAT[]             -- embedding vector
);
