SELECT file_id, file_hash, client_id, original_filename, file_path, file_size, upload_date, metadata 
FROM files 
ORDER BY {order_by} 
{limit_clause}