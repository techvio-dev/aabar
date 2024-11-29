from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import hashlib

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store coordinates
current_coordinates = {"lat": None, "lon": None}
users_db = {}

class CoordinatesModel(BaseModel):
    lat: float
    lon: float

@app.post("/set_coordinates")
async def set_coordinates(coords: CoordinatesModel):
    current_coordinates["lat"] = coords.lat
    current_coordinates["lon"] = coords.lon
    return {"status": "success"}

@app.post("/clear_coordinates")
async def clear_coordinates():
    """Clears the stored coordinates."""
    current_coordinates["lat"] = None
    current_coordinates["lon"] = None
    return {"status": "cleared"}

@app.get("/get_coordinates")
async def get_coordinates():
    return current_coordinates

class User(BaseModel):
    username: str
    password: str

@app.post("/signup")
def signup(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    # Store hashed password
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    users_db[user.username] = hashed_password
    return {"success": True, "message": "Account created successfully"}

@app.post("/login")
def login(user: User):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    if users_db.get(user.username) == hashed_password:
        return {"success": True, "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
