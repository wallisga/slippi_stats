UPDATE {api_keys_table}
SET api_key = ?, created_at = ?, expires_at = ?
WHERE client_id = ?