SELECT file_id, file_hash, client_id, original_filename, file_path, file_size, upload_date, metadata
FROM files 
WHERE client_id = ?
ORDER BY upload_date DESC
{limit_clause}