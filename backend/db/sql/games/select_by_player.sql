-- Get all games for a specific player
-- Parameters: player_tag

SELECT DISTINCT g.*
FROM games g, json_each(g.player_data) p
WHERE json_extract(p.value, '$.player_tag') = ?
ORDER BY datetime(g.start_time) DESC