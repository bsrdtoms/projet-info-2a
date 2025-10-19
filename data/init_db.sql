DROP SCHEMA IF EXISTS project CASCADE;
CREATE SCHEMA project;

--------------------------------------------------------------
-- Extension pgvector pour recherche sémantique
--------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS vector;

--------------------------------------------------------------
-- Types d Attaques
--------------------------------------------------------------

DROP TABLE IF EXISTS project.cards CASCADE ;


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
    embedding_of_text vector(1024)        -- embedding vector (pgvector)
);

--------------------------------------------------------------
-- Index pour accélérer les recherches sémantiques
--------------------------------------------------------------
CREATE INDEX IF NOT EXISTS cards_embedding_idx 
ON project.cards 
USING ivfflat (embedding_of_text vector_cosine_ops)
WITH (lists = 100);

-- Index pour les recherches par nom
CREATE INDEX IF NOT EXISTS cards_name_idx 
ON project.cards (name);