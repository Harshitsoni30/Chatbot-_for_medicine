from app.db.sessions import  user_collection, bot_prompt_collection
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.validations.token_auth import  decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
blacklisted_tokens = set()

# Updating user's password by hashing the new password before storing it securely
def register_password(password:str):
    return pwd_context.hash(password)

# Adding a new user entry to the database with all required user details
async def create_user(user):
    user['password'] = register_password(user['password'])
    result = await user_collection.insert_one(user)
    return str(result.inserted_id)

# Retrieving the email address of a user from the database
async def get_user_by_email(email: str):
    return await user_collection.find_one({"email": email})

# Retrieving the username of a user from the database
async def get_user_by_username(username:str):
    return await user_collection.find_one({"username":username})

# Hashing the plain password and comparing it with the stored hashed password to verify user login
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Verify the user's token to authenticate access for other APIs;
# if the token is invalid or expired, deny access with an invalid token response
async def get_current_user(token: str=Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401 , detail="Invalid or expired token")
    
    user = await user_collection.find_one({'email':payload.get("email")})

    if not user:
        raise HTTPException(status_code=401 , detail="user not found")
    user["token"] = token
    return user

# Generate a title for the chat session based on the user's first query input
def generate_title(prompt: str) -> str:
    title = prompt.strip().split('.')[0] 
    if len(title.split()) > 8:
        title = ' '.join(title.split()[:8])
    return title.capitalize()

# Retrieving data related to agent.py from the database
async def get_bot_by_id(bot_id: int):
    return await bot_prompt_collection.find_one({"id": bot_id})





