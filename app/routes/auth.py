from fastapi import APIRouter, HTTPException
from app.db.mongo import users
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET = "chainguard-secret-key"

def hash_password(pw):
    return pwd_context.hash(pw)

def verify_password(pw, hashed):
    return pwd_context.verify(pw, hashed)


@router.post("/signup")
def signup(data: dict):
    if users.find_one({"email": data["email"]}):
        raise HTTPException(400, "User already exists")

    users.insert_one({
        "email": data["email"],
        "password": hash_password(data["password"])
    })

    return {"msg": "User created"}


@router.post("/login")
def login(data: dict):
    user = users.find_one({"email": data["email"]})

    if not user or not verify_password(data["password"], user["password"]):
        raise HTTPException(401, "Invalid credentials")

    token = jwt.encode(
        {
            "sub": user["email"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        },
        SECRET,
        algorithm="HS256"
    )

    return {"access_token": token}