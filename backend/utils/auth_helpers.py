import bcrypt
import jwt
from datetime import datetime, timedelta
from ..config import Config

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt and return the hashed string."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain password against the hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_jwt(user_id: int) -> str:
    """Generate a JWT token for the given user ID.

    The token expires in 1 hour.
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token
