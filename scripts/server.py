import json
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from studySpotRecommender.storage.sqliteRepo import SQLiteRepository


app = FastAPI()
DB_PATH = "data/studySpots.db"
repo = SQLiteRepository(DB_PATH)
repo.initialize()


class UserPreferences(BaseModel):
    username: str
    noise_level: float
    max_distance: float
    amenities: Dict[str, int]
    location_type: Dict[str, int]

class LoginRequest(BaseModel):
    username: str
    password: str

class BookmarkRequest(BaseModel):
    username: str
    spot_key: str


@app.post("/login")
async def login(req: LoginRequest):
    # TODO: Check if user exists, get user preferences, save username somewhere
    # TODO: fix mismatching datatypes
    
    return {"exists": False, "message": "New profile created"}

@app.post("/save_preferences")
async def save_preferences(prefs: UserPreferences):
    try:
        # TODO: update user preferences in database
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/bookmarks/add")
async def add_bookmark(req: BookmarkRequest):
    try:
        repo.addBookmark(req.username, req.spot_key)
        return {"status": "success", "message": f"Bookmarked {req.spot_key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/bookmarks/remove")
async def remove_bookmark(req: BookmarkRequest):
    try:
        repo.removeBookmark(req.username, req.spot_key)
        return {"status": "success", "message": f"Removed {req.spot_key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))