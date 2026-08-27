from pydantic import BaseModel, EmailStr, Field, model_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'RegisterRequest':
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    new_password_confirm: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode='after')
    def check_new_passwords_match(self) -> 'ChangePasswordRequest':
        if self.new_password != self.new_password_confirm:
            raise ValueError('New passwords do not match')
        return self