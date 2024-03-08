from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database_con import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

#Initialize the google drive API
SERVICE_ACCOUNT_FILE = 'credentials.json'
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
drive_service = build('drive', 'v3', credentials=credentials)

#Initialize FastAPI router
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

#load secret key and algorithm for JWT
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
#OAuth2 password bearer for token URL
oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')

#pydantic model for creating a user
class CreateUserRequest(BaseModel):
    username: str
    password: str

#pydantic model for verifying login email id with google drive folder email id 
class Verify(BaseModel):
    token: str
    google_drive_folder_id: str

#pydantic model for token response
class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

#annotate the dependency for dependency injection
db_dependency= Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_users(db:db_dependency, create_user_request: CreateUserRequest):
    #create a new user
    create_user_model=Users(
        username=create_user_request.username,
        #applying password hashing before storing it in database for security reasons
        hash_password=bcrypt_context.hash(create_user_request.password),
    )
    #stores new user in database
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    #calling a method to authenticate user
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user. ')
    #calling a method for creating token after successfully found user in database
    token = create_access_token(user.username, user.id, timedelta(minutes=30))

    return {'access_token': token, 'token_type': 'bearer'}


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    #inside verify method password will auto converted to hash password and then it will be matched with hash password stored in database
    if not bcrypt_context.verify(password, user.hash_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    #encode method do encoding with help of secret key and algorithm provided
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/google-drive", status_code=status.HTTP_200_OK)
async def user_verification(verify_user: Verify):
    try:
        #decoding the token which comes from client to get users credential
        payload = jwt.decode(verify_user.token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user. ')    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='could not validate user. ')
    
    #fetching folder id from json input
    drive_folder_id=verify_user.google_drive_folder_id
    folder_metadata = drive_service.files().get(fileId=drive_folder_id, fields='owners(emailAddress)').execute()
    #fetching email id from folders metadata
    owner_email = folder_metadata['owners'][0]['emailAddress']
    #verifying if folder email id matches with login person's email id
    if owner_email != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Owner email does not match current user.')
    
    return {'message': f"welcome: {username}" }