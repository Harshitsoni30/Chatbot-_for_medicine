from fastapi import FastAPI, HTTPException, status, Depends
from app.models.auth import UserRegistration, OTPVerifyRequest, UserLogin, Tokenforlogout, CreateSession, ChatInput, UploadPDF
from app.models.users import get_user_by_email, get_user_by_username, create_user,verify_password, get_current_user, generate_title
from app.validations.sender_email import generate_otp, send_otp_email
from app.validations.token_auth import create_access_token, decode_access_token
from jose.exceptions import JWTError
from app.db.sessions import  session_id_collection, session_title_collection
from uuid import uuid4
import os
import shutil
from datetime import datetime
from app.routers.agent import load_combined_knowledge_base, create_agent
from fastapi.responses import StreamingResponse
from fastapi import Form, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
blacklisted_tokens = set()
otp_store = {}

UPLOAD_DIRECTORY = "app/data/uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## API to register a new user with username, email, and password.
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
# API endpoint to verify the OTP response during user registration 
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

# API endpoint to authenticate a user and provide access token upon successful login
"""
Endpoint to authenticate users with their credentials (email and password).
On successful authentication, returns an access token for authorized access.
"""
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

# API endpoint to log out the authenticated user and invalidate their session/token
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


# Endpoint to generate a unique session ID for the user/client
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


# API endpoint to handle chat messages within a specific user session
@app.post("/session-chat")
async def create_session_chat(chat: ChatInput,
                            current_user: dict = Depends(get_current_user)):
    prompt = chat.prompt
    session_id = chat.session_id

    pdf_path = os.path.join(UPLOAD_DIRECTORY, f"{session_id}.pdf")
    knowledge = load_combined_knowledge_base(pdf_path)
    agent = await create_agent(knowledge=knowledge)
    existing_session = await session_title_collection.find_one({
        "session_id": session_id
    })

    full_response = ""
    async def streaming_response():
        nonlocal full_response
        print_response = agent.run(prompt, stream=True)

        for chunk in print_response:
            if chunk:
                full_response += chunk.content  
                yield chunk.content  

        user_msg = {"role": "user", "content": prompt}
        assistant_msg = {"role": "assistant", "content": full_response}

        if existing_session:
            await session_title_collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"message": {"$each": [user_msg, assistant_msg]}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        else:
            title = generate_title(prompt)
            new_session = {
                "session_id": session_id,
                "title": title,
                "message": [user_msg, assistant_msg],
                "created_at": datetime.utcnow()
            }
            await session_title_collection.insert_one(new_session)

    return StreamingResponse(
        streaming_response(),
        media_type="text/event-stream",  
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

# API endpoint to upload a PDF file for knowledge base
@app.post("/upload-pdf")
async def upload_pdf(session_id: str = Form(...),
    upload_pdf: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIRECTORY, f"{session_id}.pdf")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(upload_pdf.file, f)
    return {"message": "File uploaded successfully", "file_path": file_path}


# Display chat history
@app.get("/get-chat")
async def get_chat(
    session_id: str = Query(...),  
    current_user: dict = Depends(get_current_user)):
    query = {
        "session_id": session_id
    }
    chats_cursor = session_title_collection.find(query)
    chats_history = await chats_cursor.to_list(length=1000)

    if not chats_history:
        raise HTTPException(status_code=404, detail="No chats found for this session")
    for chat in chats_history:
        chat["id"] = str(chat["_id"])
    return {"chats": chats_history}


