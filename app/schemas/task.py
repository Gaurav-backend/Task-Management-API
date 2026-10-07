from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str):
        if not value.strip():
            raise ValueError("Title must not be blank")

        return value

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: str | None):
        if value is not None and not value.strip():
            raise ValueError("Description must not be blank")

        return value

    
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    completed: StrictBool | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str | None):
        if value is not None and not value.strip():
            raise ValueError("Title must not be blank")

        return value

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, value: str | None):
        if value is not None and not value.strip():
            raise ValueError("Description must not be blank")

        return value


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime