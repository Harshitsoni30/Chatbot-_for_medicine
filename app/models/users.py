from app.db.sessions import  user_collection, bot_prompt_collection
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.validations.token_auth import  decode_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
blacklisted_tokens = set()

#genrating hash  password
def register_password(password:str):
    return pwd_context.hash(password)

#creating user 
async def create_user(user):
    user['password'] = register_password(user['password'])
    result = await user_collection.insert_one(user)
    return str(result.inserted_id)

#get email thrwo db so we can check user is exisr or not 
async def get_user_by_email(email: str):
    return await user_collection.find_one({"email": email})

async def get_user_by_username(username:str):
    return await user_collection.find_one({"username":username})

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
async def get_current_user(token: str=Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401 , detail="Invalid or expired token")
    
    user = await user_collection.find_one({'email':payload.get("email")})

    if not user:
        raise HTTPException(status_code=401 , detail="user not found")
    user["token"] = token
    return user

def generate_title(prompt: str) -> str:
    title = prompt.strip().split('.')[0]  # till first period
    if len(title.split()) > 8:
        title = ' '.join(title.split()[:8])
    return title.capitalize()


async def get_prompt_text(prompt_id: int = 3) -> str:
    prompt_data = await bot_prompt_collection.find_one({"id": prompt_id})
    return prompt_data["prompt_text"] if prompt_data else ""

A   