from fastapi import FastAPI, status, Depends, HTTPException
import models
from database_con import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
import auth
import uvicorn

app=FastAPI()
#include the router
app.include_router(auth.router)
#create the database tables
models.Base.metadata.create_all(bind=engine)

#dependency to get a database session
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

#annotate the dependency for dependency injection
db_dependency= Annotated[Session, Depends(get_db)]
#user_dependency= Annotated[dict, Depends(get_current_user)]

@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: None, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    return {'User': user}

if __name__=='__main__':
    uvicorn.run("main:app", reload=True)