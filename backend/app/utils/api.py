import os
import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt

from app.utils.iam import IAM
from app.utils.user import User

JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12


class UserCreateRequest(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    admin: bool = False


class UserResponse(BaseModel):
    username: str
    admin: bool
    full_name: Optional[str] = None
    last_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')
router = APIRouter()


def get_iam(iam: IAM = Depends(lambda: None)) -> IAM:
    """Overridden at app startup with the real IAM instance -- see app/main.py."""
    if iam is None:
        raise RuntimeError("IAM instance not provided to API router.")
    return iam


def _get_jwt_secret() -> str:
    secret = os.getenv('JWT_SECRET')
    if not secret:
        raise RuntimeError('JWT_SECRET is not set -- cannot handle tokens.')
    return secret


def _create_access_token(username: str) -> str:
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {'sub': username, 'exp': expires_at}
    return jwt.encode(payload, _get_jwt_secret(), algorithm=JWT_ALGORITHM)


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), iam: IAM = Depends(get_iam)):
    username = form_data.username
    password = form_data.password

    if not iam.check_user(username=username, password=password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user = iam.get_user(username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='User found during verification but not during login. Internal error.',
        )

    access_token = _create_access_token(username)
    return {'access_token': access_token, 'token_type': 'bearer'}


async def get_current_user(token: str = Depends(oauth2_scheme), iam: IAM = Depends(get_iam)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = iam.get_user(username=username)
    if not user:
        raise credentials_exception
    return user


@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreateRequest,
    iam: IAM = Depends(get_iam),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin access required',
        )

    is_suitable, message = iam.is_suitable(user_data.username, user_data.password)
    if not is_suitable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    registration_success, registration_message = iam.create_user(
        username=user_data.username,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        admin=user_data.admin,
    )
    if not registration_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Registration failed: {registration_message}',
        )

    new_user = iam.get_user(user_data.username)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='User registered but could not be retrieved post-registration. Internal error.',
        )
    return new_user.to_dict()


@router.get('/users/me', response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()


@router.get('/protected_data')
async def get_protected_data(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.get_username()}! This is protected data."}
