WITH player_tags AS (
    SELECT DISTINCT json_extract(p.value, '$.player_tag') as tag
    FROM games, json_each(games.player_data) as p
    WHERE json_extract(p.value, '$.player_tag') IS NOT NULL
      AND json_extract(p.value, '$.player_tag') != ''
)
SELECT COUNT(*) as count FROM player_tags