from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

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

class CoordinatesModel(BaseModel):
    lat: float
    lon: float

@app.post("/set_coordinates")
async def set_coordinates(coords: CoordinatesModel):
    current_coordinates["lat"] = coords.lat
    current_coordinates["lon"] = coords.lon
    return {"status": "success"}

@app.get("/get_coordinates")
async def get_coordinates():
    return current_coordinates