from fastapi import FastAPI, HTTPException, status, Depends
from app.models.auth import UserRegistration, OTPVerifyRequest
from app.models.users import get_user_by_email, get_user_by_username, create_user
from app.validations.sender_email import generate_otp, send_otp_email
app = FastAPI()

otp_store = {}
@app.post("/register-otp-request")
async def register_with_otp(user :UserRegistration):
    existing_user_email = await get_user_by_email(user.email)
    existing_user_username = await get_user_by_username(user.username)
    
    if existing_user_email or existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    otp = generate_otp()
    otp_store[user.email]={
        "otp":otp,
        "user_data":user.dict()
    }
    await send_otp_email(user.email, otp)
    return {
        "message":"OTP send successfully"
    }
@app.post("/register-otp-response")
async def register_response_otp(data:OTPVerifyRequest):
    email = data.email
    otp = data.otp
    if email not in otp_store:
        raise HTTPException(status_code=404, detail="otp is expired or invalid email")
    
    stored = otp_store[email]
    if stored["otp"] != otp:
        raise HTTPException(status_code=404, detail="Invalid OTP")
    
    user_data =stored["user_data"]
    user_id =await create_user(user_data)

    del otp_store[email]

    return {
        "message":"User registered Successfully",
        "user_id":user_id
    }
