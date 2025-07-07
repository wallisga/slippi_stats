-- backend/db/sql/stats/all_players_with_stats.sql
-- FIXED: Corrected column alias issue

WITH player_games AS (
    SELECT 
        json_extract(p.value, '$.player_tag') as player_tag,
        json_extract(p.value, '$.character_name') as character_name,
        CASE WHEN json_extract(p.value, '$.result') = 'Win' THEN 1 ELSE 0 END as won,
        g.start_time
    FROM games g, json_each(g.player_data) p
    WHERE json_extract(p.value, '$.player_tag') IS NOT NULL
      AND json_extract(p.value, '$.player_tag') != ''
      AND json_extract(p.value, '$.player_tag') != 'null'
),
player_stats AS (
    SELECT 
        player_tag,
        COUNT(*) as total_games,
        SUM(won) as wins,
        MAX(start_time) as last_game
    FROM player_games
    GROUP BY player_tag
),
character_usage AS (
    SELECT 
        player_tag,
        character_name,
        COUNT(*) as char_games,
        ROW_NUMBER() OVER (PARTITION BY player_tag ORDER BY COUNT(*) DESC) as usage_rank
    FROM player_games
    WHERE character_name IS NOT NULL 
      AND character_name != ''
      AND character_name != 'null'
    GROUP BY player_tag, character_name
)
SELECT 
    ps.player_tag,
    ps.total_games,
    ps.wins,
    (ps.total_games - ps.wins) as losses,
    ROUND((CAST(ps.wins AS FLOAT) / ps.total_games) * 100, 2) as win_rate,
    ps.last_game,
    cu.character_name as most_played_character
FROM player_stats ps
LEFT JOIN character_usage cu ON ps.player_tag = cu.player_tag AND cu.usage_rank = 1
WHERE ps.total_games > 0
  AND ps.player_tag IS NOT NULL
  AND ps.player_tag != ''
ORDER BY ps.total_games DESC