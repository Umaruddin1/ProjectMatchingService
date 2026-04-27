"""Authentication schemas."""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login request payload."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response payload."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
