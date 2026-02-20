from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import requests

app = FastAPI(title="Diabetes Food Recall Tracking API")

OPENFDA_URL = "https://api.fda.gov/food/enforcement.json"

# ------------------------
# Models
# ------------------------

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)

class UserResponse(BaseModel):
    id: str
    username: str
    created_at: str

class CreateNoteRequest(BaseModel):
    text: str

class NoteResponse(BaseModel):
    id: str
    text: str
    created_at: str
    data: Optional[Dict[str, Any]] = None

class FDAQueryRequest(BaseModel):
    food_query: str
    limit: int = 5
    skip: int = 0


# ------------------------
# In-memory storage
# ------------------------

users: Dict[str, Dict] = {}
username_index: Dict[str, str] = {}
notes: Dict[str, List[Dict]] = {}

# ------------------------
# Helper functions
# ------------------------

def now():
    return datetime.utcnow().isoformat() + "Z"

def get_user(user_id: str):
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def build_search_query(food_query: str):
    q = food_query.strip().replace('"', '\\"')
    if " " in q:
        return f'product_description:"{q}"'
    return f"product_description:{q}"

def fetch_fda(food_query: str, limit: int, skip: int):
    params = {
        "search": build_search_query(food_query),
        "limit": limit,
        "skip": skip,
    }
    try:
        response = requests.get(OPENFDA_URL, params=params, timeout=10)
        data = response.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Error contacting openFDA")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="openFDA error")

    return data

def extract_fields(item):
    return {
        "product_description": item.get("product_description"),
        "recalling_firm": item.get("recalling_firm"),
        "reason_for_recall": item.get("reason_for_recall"),
        "classification": item.get("classification"),
        "recall_initiation_date": item.get("recall_initiation_date"),
    }

# ------------------------
# Endpoints
# ------------------------

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(payload: CreateUserRequest):
    if payload.username in username_index:
        raise HTTPException(status_code=409, detail="Username already exists")

    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "username": payload.username,
        "created_at": now()
    }

    users[user_id] = user
    username_index[payload.username] = user_id
    notes[user_id] = []

    return user

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: str):
    return get_user(user_id)

@app.post("/users/{user_id}/notes", response_model=NoteResponse, status_code=201)
def add_note(user_id: str, payload: CreateNoteRequest):
    get_user(user_id)

    note = {
        "id": str(uuid.uuid4()),
        "text": payload.text,
        "created_at": now(),
        "data": None
    }

    notes[user_id].append(note)
    return note

@app.get("/users/{user_id}/notes")
def list_notes(user_id: str):
    get_user(user_id)
    return {"user_id": user_id, "notes": notes[user_id]}

@app.post("/users/{user_id}/fda-food-recalls", status_code=201)
def query_fda_and_save(user_id: str, payload: FDAQueryRequest):
    get_user(user_id)

    fda_data = fetch_fda(payload.food_query, payload.limit, payload.skip)
    results = fda_data.get("results", [])
    extracted = [extract_fields(r) for r in results]

    note_text = f"FDA recall lookup for '{payload.food_query}'. Results returned: {len(extracted)}"

    note = {
        "id": str(uuid.uuid4()),
        "text": note_text,
        "created_at": now(),
        "data": extracted
    }

    notes[user_id].append(note)

    return {
        "query": payload.food_query,
        "results": extracted,
        "saved_note_id": note["id"]
    }