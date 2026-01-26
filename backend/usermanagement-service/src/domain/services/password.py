import bcrypt
import hashlib

class PasswordService:
    """Service for hashing and verifying passwords using bcrypt"""

    def hash_password(self, password: str) -> str:
        sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(sha256_hash.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        return bcrypt.checkpw(
            sha256_hash.encode('utf-8'),
            hashed_password.encode('utf-8')
        )