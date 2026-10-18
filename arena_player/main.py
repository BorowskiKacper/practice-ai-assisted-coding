from contextlib import asynccontextmanager
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .db import cache, db, ensure_indexes

def oid(value: str) -> ObjectId:
    try: return ObjectId(value)
    except Exception: raise HTTPException(404, "resource not found")
def expose(doc):
    if doc is None: return None
    doc=dict(doc); doc["id"]=str(doc.pop("_id")); return doc

class CompanyIn(BaseModel): name: str = Field(min_length=2)
class ModeIn(BaseModel): slug: str = Field(pattern=r"^[a-z0-9-]+$"); display_name: str
class PlayerIn(BaseModel): external_id: str; display_name: str
class QueueIn(BaseModel): company_id: str; mode_id: str; player_id: str
class ResultIn(BaseModel): winner_id: str; loser_id: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_indexes(); yield
app=FastAPI(title="Arena Player", lifespan=lifespan)

@app.get("/health")
def health(): db.command("ping"); cache.ping(); return {"status":"ok"}
@app.post("/companies",status_code=201)
def company(body:CompanyIn):
    doc={"name":body.name,"created_at":datetime.now(timezone.utc)}; r=db.companies.insert_one(doc); doc["_id"]=r.inserted_id; return expose(doc)
@app.post("/companies/{company_id}/modes",status_code=201)
def mode(company_id:str,body:ModeIn):
    if not db.companies.find_one({"_id":oid(company_id)}): raise HTTPException(404,"company not found")
    doc={"company_id":company_id,"slug":body.slug,"display_name":body.display_name}; r=db.game_modes.insert_one(doc); doc["_id"]=r.inserted_id; return expose(doc)
@app.post("/companies/{company_id}/players",status_code=201)
def player(company_id:str,body:PlayerIn):
    if not db.companies.find_one({"_id":oid(company_id)}): raise HTTPException(404,"company not found")
    doc={"company_id":company_id,"external_id":body.external_id,"display_name":body.display_name}; r=db.players.insert_one(doc); doc["_id"]=r.inserted_id; return expose(doc)
def rank(company,mode,player):
    return db.rankings.find_one_and_update({"company_id":company,"mode_id":mode,"player_id":player},{"$setOnInsert":{"rating":1000,"wins":0,"losses":0}},upsert=True,return_document=True)
@app.post("/queue/join",status_code=202)
def join(body:QueueIn):
    if not db.game_modes.find_one({"_id":oid(body.mode_id),"company_id":body.company_id}): raise HTTPException(404,"mode not found")
    if not db.players.find_one({"_id":oid(body.player_id),"company_id":body.company_id}): raise HTTPException(404,"player not found")
    r=rank(body.company_id,body.mode_id,body.player_id); key=f"queue:{body.company_id}:{body.mode_id}"; cache.zadd(key,{body.player_id:r["rating"]}); return {"queue_key":key,"rating":r["rating"]}
@app.post("/queue/match")
def match(company_id:str,mode_id:str):
    key=f"queue:{company_id}:{mode_id}"
    # DELIBERATE BUG: a concurrent worker can read these players before removal.
    ids=cache.zrange(key,0,1)
    if len(ids)<2: raise HTTPException(409,"not enough queued players")
    cache.zrem(key,*ids)
    doc={"company_id":company_id,"mode_id":mode_id,"player_ids":ids,"status":"pending","created_at":datetime.now(timezone.utc)}; r=db.matches.insert_one(doc); doc["_id"]=r.inserted_id; return expose(doc)
@app.get("/companies/{company_id}/leaderboard/{mode_id}")
def board(company_id:str,mode_id:str):
    # DELIBERATE BUG: ascending rating makes lowest rating rank first.
    return [expose(x) for x in db.rankings.find({"company_id":company_id,"mode_id":mode_id}).sort("rating",1).limit(100)]
@app.get("/companies/{company_id}/matches/{match_id}")
def get_match(company_id:str,match_id:str):
    # DELIBERATE BUG: tenant filter is absent.
    doc=db.matches.find_one({"_id":oid(match_id)})
    if not doc: raise HTTPException(404,"match not found")
    return expose(doc)
@app.post("/matches/{match_id}/result")
def result(match_id:str,body:ResultIn):
    doc=db.matches.find_one({"_id":oid(match_id)})
    if not doc: raise HTTPException(404,"match not found")
    if {body.winner_id,body.loser_id} != set(doc["player_ids"]): raise HTTPException(422,"result players do not match")
    # DELIBERATE BUG: retries apply deltas again because completion is not claimed first.
    for player_id,delta,field in ((body.winner_id,25,"wins"),(body.loser_id,-25,"losses")):
        db.rankings.update_one({"company_id":doc["company_id"],"mode_id":doc["mode_id"],"player_id":player_id},{"$inc":{"rating":delta,field:1}},upsert=True)
    db.matches.update_one({"_id":doc["_id"]},{"$set":{"status":"complete","winner_id":body.winner_id}}); return {"status":"recorded"}
