from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AbstractReadSchemas(BaseModel):
    """
    Represents a base schema for models with common fields such as creation timestamp,
    update timestamp, and deletion status.
    """

    is_deleted: bool

    class Config:
        from_attributes = True


class AbstractWriteUpdateSchemas(BaseModel):
    """
    Represents a base schema for models with common fields.
    """

    class Config:
        from_attributes = True
