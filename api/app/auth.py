import os, datetime
from jose import jwt, JWTError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-please")
ALGO = "HS256"
EXPIRES_MIN = 60 * 24

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd_context.verify(p, h)

def make_token(user_id: int, email: str) -> str:
    payload = {"sub": str(user_id), "email": email, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=EXPIRES_MIN)}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGO)

def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGO])
    except JWTError:
        return None
