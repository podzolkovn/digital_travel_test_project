from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AbstractReadSchemas(BaseModel):
    """
    Represents a base schema for models with common fields such as creation timestamp,
    update timestamp, and deletion status.
    """

    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class AbstractWriteUpdateSchemas(BaseModel):
    """
    Represents a base schema for models with common fields.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )
