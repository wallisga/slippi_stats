SELECT client_id, COUNT(*) as file_count, SUM(file_size) as client_size
FROM files 
GROUP BY client_id 
ORDER BY file_count DESC