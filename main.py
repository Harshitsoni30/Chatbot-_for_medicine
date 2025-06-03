from fastapi import FastAPI, HTTPException, status, Depends
from app.models.auth import UserRegistration, OTPVerifyRequest, UserLogin, Tokenforlogout, CreateSession
from app.models.users import get_user_by_email, get_user_by_username, create_user,verify_password, get_current_user
from app.validations.sender_email import generate_otp, send_otp_email
from app.validations.token_auth import create_access_token, decode_access_token
from jose.exceptions import JWTError
from app.db.sessions import  session_id_collection
from uuid import uuid4



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

    

    return {
        "message":"User registered Successfully",
        "user_id":user_id
    }
@app.post("/login")
async def login(user:UserLogin):
    db_user = await get_user_by_email(user.email)
    if not db_user:
        raise HTTPException(status_code=404 , detail="User not found")
    if not verify_password(user.password, db_user['password']):
        raise HTTPException(status_code=401, detail="Inavlid password")
    
    token = create_access_token(
        data={"email":user.email},
        
    )
    return {
        "token":token,
        "email": db_user["email"],
        "username": db_user["username"]
    }

blacklisted_tokens = set()

@app.post("/logout")
async def logout(user:Tokenforlogout,
                current_user: dict = Depends(get_current_user)):
    
    token = current_user.get("token")
    if user.email != current_user.get("email"):
        raise HTTPException(status_code=401, detail="Invalid Emial")
   
    if token in blacklisted_tokens:
        raise HTTPException(status_code=401, detail="already blacklisted")

    blacklisted_tokens.add(token)

    return {"message": "Logout Successfully"}

@app.post("/get-session-id")
async def get_session_id(current_user : dict = Depends(get_current_user)):
    session_id = str(uuid4())
    session = CreateSession(
        session_id=session_id,
        user_email = current_user['email']
    )
    await session_id_collection.insert_one(session.dict())
    return {
        "message":"Session id is created",
        "session_id":session_id
    }
