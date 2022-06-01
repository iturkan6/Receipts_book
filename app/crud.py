from typing import Union

from fastapi import HTTPException, status
from passlib.context import CryptContext

from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# password hashing methods

def verify(plain_password, given_password):
    return pwd_context.verify(plain_password, given_password)


def hash_password(password: str):
    return pwd_context.hash(password)


# --------------------------


# user methods

def get_user(user_id):
    return models.User.filter(models.User.id == user_id).first()


def get_user_by_username(username: str):
    return models.User.filter(models.User.username == username).first()


def create_user(user: schemas.UserCreate):
    db_user = get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist")
    hashed_password = hash_password(user.password)
    created_user = models.User(**user.dict(), hashed_password=hashed_password)
    created_user.save()
    return created_user


def authenticate(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist")
    if not verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong username or password")
    return user


# --------------------------


# receipts methods

def get_receipt_by_id(receipt_id, owner_id: Union[int, None] = None):
    receipt = models.Receipt.filter(
        (models.Receipt.id == receipt_id) &
        ((models.Receipt.is_public == 1) | (models.Receipt.owner_id == owner_id))).first()
    return receipt


def get_receipt_by_title(title, owner_id: Union[int, None] = None):
    receipt = models.Receipt.filter(
        (models.Receipt.title == title) &
        ((models.Receipt.is_public == 1) | (models.Receipt.owner_id == owner_id))).first()
    return receipt


def get_receipt(title: Union[str, None] = None, receipt_id: Union[int, None] = None, owner_id: Union[int, None] = None):
    if receipt_id:
        receipt = get_receipt_by_id(receipt_id, owner_id)
        if receipt:
            return receipt
    elif title:
        receipt = get_receipt_by_title(title, owner_id)
        if receipt:
            return receipt
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No receipt with such id or title")


def get_receipts(user_id: Union[int, None] = None):
    if user_id:
        return list(models.Receipt.filter(models.Receipt.owner_id == user_id))
    return list(models.Receipt.filter(models.Receipt.is_public == 1))


def create_receipt(receipt: schemas.ReceiptCreate, owner_id: int):
    receipt_db = models.Receipt.create(
        title=receipt.title,
        ingredients=receipt.ingredients,
        owner_id=owner_id,
        description=receipt.description)
    return receipt_db

# --------------------------
