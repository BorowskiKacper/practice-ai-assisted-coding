# Background

The API stores durable company, player, mode, match, and ranking records in MongoDB. Redis sorted sets implement mode-specific waiting queues; the score is a player's current rating. Ratings begin at 1000. A completed match awards its winner 25 points and removes 25 from its loser.

All records are tenant scoped by `company_id`. A game mode belongs to one company, and a match belongs to one company and one mode. Queue matching is expected to consume two waiting players once, even if multiple API instances run simultaneously.
