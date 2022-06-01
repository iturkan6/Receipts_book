from typing import Union

from fastapi import FastAPI, Depends, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.responses import JSONResponse

import crud
import database
import models
import schemas

database.db.connect()
database.db.create_tables([models.User, models.Receipt])
database.db.close()

app = FastAPI()


# def get_db(db_state=Depends(reset_db_state)):
#     try:
#         database.db.connect()
#         yield
#     finally:
#         if not database.db.is_closed():
#             database.db.close()


@AuthJWT.load_config
def get_config():
    return schemas.Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.get("/user", response_model=schemas.User)
def get_user(auth: AuthJWT = Depends()):
    auth.jwt_required()
    user_id = auth.get_jwt_subject()
    current_user = crud.get_user(user_id)
    return current_user


@app.post("/login")
def login(user: schemas.UserLogin, auth: AuthJWT = Depends()):
    user = crud.authenticate(user.username, user.password)
    access_token = auth.create_access_token(subject=user.id, fresh=True)
    refresh_token = auth.create_refresh_token(subject=user.id)
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/user", response_model=schemas.User)
def create_user(user: schemas.UserCreate):
    user_db = crud.create_user(user)
    return user_db


@app.post("/refresh")
def refresh(auth: AuthJWT = Depends()):
    auth.jwt_refresh_token_required()
    current_user = auth.get_jwt_subject()
    new_access_token = auth.create_access_token(subject=current_user, fresh=False)
    return {"access_token": new_access_token}


@app.get("/receipts/my", response_model=list[schemas.Receipt])
def read_receipts(auth: AuthJWT = Depends()):
    auth.jwt_required()
    user_id = auth.get_jwt_subject()
    receipts = crud.get_receipts(user_id=user_id)
    return receipts


@app.get("/receipts", response_model=list[schemas.Receipt])
def read_receipts():
    receipts = crud.get_receipts()
    return receipts


@app.get("/receipt", response_model=schemas.Receipt)
def read_receipt(receipt_id: Union[int, None] = None, title: Union[str, None] = None, auth: AuthJWT = Depends()):
    auth.jwt_optional()
    user_id = auth.get_jwt_subject()
    receipt = crud.get_receipt(title=title, receipt_id=receipt_id, owner_id=user_id)
    return receipt


@app.post("/receipt", response_model=schemas.Receipt)
def create_receipt(receipt: schemas.ReceiptCreate, auth: AuthJWT = Depends()):
    auth.jwt_required()
    user_id = auth.get_jwt_subject()
    receipt_db = crud.create_receipt(receipt=receipt, owner_id=user_id)
    return receipt_db
