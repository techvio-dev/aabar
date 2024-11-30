from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib

app = FastAPI()

DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    nationality = Column(String, nullable=False)
    id_number = Column(String, nullable=False)
    city = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    gender: str
    nationality: str
    id_number: str
    city: str

class UserLogin(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/signup")
def signup(user: UserCreate, db: SessionLocal = Depends(get_db)):
    # Check if the user already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="User already exists")
    
        new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
        nationality=user.nationality,
        id_number=user.id_number,
        city=user.city,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": True, "message": "Account created successfully"}

@app.post("/login")
def login(user: UserLogin, db: SessionLocal = Depends(get_db)):
    # Find the user in the database
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or db_user.hashed_password != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"success": True, "message": "Login successful"}

class CoordinatesModel(BaseModel):
    lat: float
    lon: float

current_coordinates = {"lat": None, "lon": None}

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
