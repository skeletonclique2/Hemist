"""
Security utilities for AI Agents System
Handles JWT creation/verification and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional, Union, List
import structlog
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Bearer token security scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password.
        
    Returns:
        bool: True if the password matches, False otherwise.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error("Password verification failed", error=str(e))
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a plain password.
    
    Args:
        password (str): The plain text password.
        
    Returns:
        str: The hashed password.
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error("Password hashing failed", error=str(e))
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[timedelta]): The expiration time delta.
        
    Returns:
        str: The encoded JWT token.
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error("JWT token creation failed", error=str(e))
        raise

def verify_access_token(token: str) -> Optional[dict]:
    """
    Verify a JWT access token and return the payload.
    
    Args:
        token (str): The JWT token to verify.
        
    Returns:
        Optional[dict]: The decoded payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error("JWT token verification failed", error=str(e))
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get the current authenticated user from the JWT token.
    
    Args:
        credentials (HTTPAuthorizationCredentials): The bearer token credentials.
        
    Returns:
        dict: The user data from the token payload.
        
    Raises:
        HTTPException: If the token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # In a real implementation, you would fetch user data from a database
    # For now, we'll just return the payload
    return payload

# Example user data for demonstration (in production, this would come from a database)
EXAMPLE_USERS = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("adminpassword"),  # In production, never hardcode passwords
        "role": "admin"
    },
    "user": {
        "username": "user",
        "hashed_password": get_password_hash("userpassword"),  # In production, never hardcode passwords
        "role": "user"
    },
    "demo": {
        "username": "demo",
        "hashed_password": get_password_hash("demo123"),  # In production, never hardcode passwords
        "role": "user"
    },
    "skeletoncliqs": {
        "username": "skeletoncliqs",
        "hashed_password": get_password_hash("Lolxxxno1"),
        "role": "admin"
    }
}

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authenticate a user by username and password.
    
    Args:
        username (str): The username.
        password (str): The plain text password.
        
    Returns:
        Optional[dict]: The user data if authentication is successful, None otherwise.
    """
    user = EXAMPLE_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

class RoleChecker:
    """
    Dependency class to check if the current user has the required role.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(RoleChecker(["admin"]))])
    """
    
    def __init__(self, allowed_roles: List[str]):
        """
        Initialize the RoleChecker with allowed roles.
        
        Args:
            allowed_roles (List[str]): List of roles that are allowed to access the endpoint.
        """
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        """
        Check if the current user has one of the allowed roles.
        
        Args:
            current_user (dict): The current authenticated user from JWT token.
            
        Returns:
            dict: The current user if authorized.
            
        Raises:
            HTTPException: If the user doesn't have the required role.
        """
        user_role = current_user.get("role", "")
        
        if user_role not in self.allowed_roles:
            logger.warning(
                "Access denied - insufficient permissions",
                username=current_user.get("sub"),
                user_role=user_role,
                required_roles=self.allowed_roles
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this resource"
            )
        
        return current_user

def create_user(username: str, password: str, role: str = "user") -> dict:
    """
    Create a new user (for demonstration - in production, save to database).
    
    Args:
        username (str): The username.
        password (str): The plain text password.
        role (str): The user role (default: "user").
        
    Returns:
        dict: The created user data.
    """
    if username in EXAMPLE_USERS:
        raise ValueError(f"User {username} already exists")
    
    user = {
        "username": username,
        "hashed_password": get_password_hash(password),
        "role": role
    }
    
    # In production, save to database
    EXAMPLE_USERS[username] = user
    
    logger.info(f"User created: {username} with role: {role}")
    return {"username": username, "role": role}
