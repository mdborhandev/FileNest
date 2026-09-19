from pydantic import BaseModel


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ForgotPasswordResponse(BaseModel):
    detail: str


class ResetPasswordResponse(BaseModel):
    detail: str
