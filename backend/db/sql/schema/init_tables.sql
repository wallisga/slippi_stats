-- Create clients table
CREATE TABLE IF NOT EXISTS clients (
    client_id TEXT PRIMARY KEY,
    hostname TEXT,
    platform TEXT,
    version TEXT,
    registration_date TEXT,
    last_active TEXT
);

-- Create games table
CREATE TABLE IF NOT EXISTS games (
    game_id TEXT PRIMARY KEY,
    client_id TEXT,
    start_time TEXT,
    last_frame INTEGER,
    stage_id INTEGER,
    player_data TEXT,
    upload_date TEXT,
    game_type TEXT,
    FOREIGN KEY (client_id) REFERENCES clients (client_id)
);

-- Create API keys table (uses config.API_KEYS_TABLE for table name)
CREATE TABLE IF NOT EXISTS {api_keys_table} (
    client_id TEXT PRIMARY KEY,
    api_key TEXT UNIQUE,
    created_at TEXT,
    expires_at TEXT,
    FOREIGN KEY (client_id) REFERENCES clients (client_id)
);

-- Create files table
CREATE TABLE IF NOT EXISTS files (
    file_id TEXT PRIMARY KEY,
    file_hash TEXT UNIQUE NOT NULL,
    client_id TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    upload_date TEXT NOT NULL,
    metadata TEXT,
    FOREIGN KEY (client_id) REFERENCES clients (client_id)
);