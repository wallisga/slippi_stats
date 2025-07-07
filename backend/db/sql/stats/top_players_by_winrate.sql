WITH player_stats AS (
    SELECT 
        json_extract(p.value, '$.player_tag') as player_tag,
        COUNT(*) as total_games,
        SUM(CASE WHEN json_extract(p.value, '$.result') = 'Win' THEN 1 ELSE 0 END) as wins
    FROM games g, json_each(g.player_data) p
    WHERE json_extract(p.value, '$.player_tag') IS NOT NULL
      AND json_extract(p.value, '$.player_tag') != ''
    GROUP BY json_extract(p.value, '$.player_tag')
    HAVING total_games >= ?
)
SELECT 
    player_tag,
    total_games,
    wins,
    ROUND((CAST(wins AS FLOAT) / total_games) * 100, 2) as win_rate
FROM player_stats
ORDER BY win_rate DESC, total_games DESC
LIMIT ?