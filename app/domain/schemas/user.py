from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """
    Schema for reading user information, including the user's role.
    """

    role: str


class UserCreate(schemas.BaseUserCreate):
    """
    Schema for creating a new user with default fields from BaseUserCreate.
    """

    pass
