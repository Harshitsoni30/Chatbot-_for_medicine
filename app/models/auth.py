from pydantic import BaseModel, EmailStr, Field
from fastapi import Form, File, UploadFile

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

class CreateSession(BaseModel):
    session_id: str
    user_email: EmailStr

class ChatInput(BaseModel):
    prompt:str
    session_id:str

class UploadPDF(BaseModel):
    session_id: str = Form(...),
    uploaded_pdf: UploadFile = File(...)
