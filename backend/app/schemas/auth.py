from pydantic import BaseModel, EmailStr, Field, field_validator

USERNAME_PATTERN = r"^[a-z0-9_]{3,30}$"


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(pattern=USERNAME_PATTERN)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username", mode="before")
    @classmethod
    def _lowercase_username(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, description="Email address or username")
    password: str = Field(min_length=1)
