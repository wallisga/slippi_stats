SELECT game_id, client_id, start_time, last_frame, stage_id, player_data, upload_date, game_type 
FROM games 
ORDER BY {order_by} 
{limit_clause}