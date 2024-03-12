from fastapi import FastAPI, status, Depends, HTTPException
import models
from database_con import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
import auth
import uvicorn
import subprocess
import psutil

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

#get information about all processes with a 'cmdline' attribute that is not empty
streamlit_processes = [p.info for p in psutil.process_iter(attrs=['cmdline']) if p.info['cmdline'] and 'app.py' in p.info['cmdline']]

#check if there are no Streamlit processes running
if not streamlit_processes:
    #run the streamlit app if it's not already running
    subprocess.Popen(["streamlit", "run", "app.py"])
if __name__=='__main__':
    uvicorn.run("main:app", reload=True)