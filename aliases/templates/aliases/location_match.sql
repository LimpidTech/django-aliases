SELECT * FROM aliases_url WHERE
    `location` LIKE "%s%%"

ORDER BY LENGTH(location) LIMIT 1
