import os
from pymongo import MongoClient
import redis

mongo = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
db = mongo[os.getenv("MONGODB_DB", "arena_player")]
cache = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

def ensure_indexes():
    db.game_modes.create_index([("company_id", 1), ("slug", 1)], unique=True)
    db.players.create_index([("company_id", 1), ("external_id", 1)], unique=True)
    db.rankings.create_index([("company_id", 1), ("mode_id", 1), ("player_id", 1)], unique=True)
