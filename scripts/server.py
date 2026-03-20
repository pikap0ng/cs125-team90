import json
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from studySpotRecommender.storage.sqliteRepo import SQLiteRepository


app = FastAPI()
DB_PATH = "data/studySpots.db"


class UserPreferences(BaseModel):
    username: str
    noise_level: float
    max_distance: float
    amenities: Dict[str, int]
    location_type: Dict[str, int]

class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(req: LoginRequest):
    # TODO: Check if user exists, get user preferences, save username somewhere
    
    # if row:
    #     return {
    #         "exists": True,
    #         "preferences": {
    #             "noise_level": row[1],
    #             "max_distance": row[2],
    #             "amenities": json.loads(row[3]),
    #             "location_type": json.loads(row[4])
    #         }
    #     }
    return {"exists": False, "message": "New profile created"}

@app.post("/save_preferences")
async def save_preferences(prefs: UserPreferences):
    try:
        # TODO: update user preferences in database
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))