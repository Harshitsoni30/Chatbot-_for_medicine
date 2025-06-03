from pydantic import BaseModel, EmailStr, Field

class UserRegistration(BaseModel):
    username:str = Field(..., min_lenght=3)
    email:EmailStr
    password:str =Field(..., min_length =6)

class OTPVerifyRequest(BaseModel):
    email:EmailStr
    otp:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class Tokenforlogout(BaseModel):
    email:EmailStr
    