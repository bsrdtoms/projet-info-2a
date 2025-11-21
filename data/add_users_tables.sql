--------------------------------------------------------------
-- Users table
--------------------------------------------------------------
CREATE TABLE IF NOT EXISTS project.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('client', 'game_designer', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index to accelerate email searches
CREATE INDEX IF NOT EXISTS users_email_idx ON project.users(email);

--------------------------------------------------------------
-- Sessions table
--------------------------------------------------------------
CREATE TABLE IF NOT EXISTS project.sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES project.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Index to accelerate user_id searches
CREATE INDEX IF NOT EXISTS sessions_user_id_idx ON project.sessions(user_id);

--------------------------------------------------------------
-- Favorites table (many-to-many relationship)
--------------------------------------------------------------
CREATE TABLE IF NOT EXISTS project.favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES project.users(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES project.cards(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, card_id)
);

-- Index to accelerate searches
CREATE INDEX IF NOT EXISTS favorites_user_id_idx ON project.favorites(user_id);
CREATE INDEX IF NOT EXISTS favorites_card_id_idx ON project.favorites(card_id);

--------------------------------------------------------------
-- Search history table
--------------------------------------------------------------
CREATE TABLE IF NOT EXISTS project.search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES project.users(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    query_embedding vector(1024),
    result_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index to accelerate searches by user
CREATE INDEX IF NOT EXISTS search_history_user_id_idx ON project.search_history(user_id);

--------------------------------------------------------------
-- Function to automatically update updated_at
--------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for the users table
DROP TRIGGER IF EXISTS update_users_updated_at ON project.users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON project.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

--------------------------------------------------------------
-- Insert a default admin (password: admin123)
--------------------------------------------------------------
INSERT INTO project.users (email, password_hash, first_name, last_name, user_type)
VALUES (
    'admin@magicsearch.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7667iSVZLO',
    'Admin',
    'System',
    'admin'
) ON CONFLICT (email) DO NOTHING;