from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    """Schema for returning user data without sensitive password fields."""

    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for bearer authentication token response."""

    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    """Schema for task creation request."""

    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    """Schema for updating task attributes optionally."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    due_date: Optional[date] = None
    is_completed: Optional[bool] = None


class TaskOut(BaseModel):
    """Schema for returning task details."""

    id: int
    title: str
    description: Optional[str] = None
    is_completed: bool
    due_date: Optional[date] = None
    created_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
