-- Performance indexes for games table
CREATE INDEX IF NOT EXISTS idx_games_start_time ON games (start_time);
CREATE INDEX IF NOT EXISTS idx_games_client_id ON games (client_id);
CREATE INDEX IF NOT EXISTS idx_games_upload_date ON games (upload_date);

-- Performance indexes for API keys table
CREATE INDEX IF NOT EXISTS idx_api_keys_key ON {api_keys_table} (api_key);

-- Performance indexes for clients table
CREATE INDEX IF NOT EXISTS idx_clients_last_active ON clients (last_active);

-- Performance indexes for files table
CREATE INDEX IF NOT EXISTS idx_files_hash ON files (file_hash);
CREATE INDEX IF NOT EXISTS idx_files_client_id ON files (client_id);
CREATE INDEX IF NOT EXISTS idx_files_upload_date ON files (upload_date);
CREATE INDEX IF NOT EXISTS idx_files_original_filename ON files (original_filename);