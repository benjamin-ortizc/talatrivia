from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# https://www.rfc-editor.org/rfc/rfc6749.html#section-4.2.2
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
