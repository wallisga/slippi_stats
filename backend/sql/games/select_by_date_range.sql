SELECT game_id, client_id, start_time, last_frame, stage_id, player_data, upload_date, game_type
FROM games 
WHERE datetime(start_time) BETWEEN datetime(?) AND datetime(?)
ORDER BY datetime(start_time) DESC