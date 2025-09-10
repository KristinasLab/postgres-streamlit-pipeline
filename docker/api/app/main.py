from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import Optional
from . import models, schemas, crud
from .database import SessionLocal, engine
from .schemas import Company, Headcount, Revenue, Dim_Date
models.Base.metadata.create_all(bind=engine)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # oder spezifisch: ["https://deine-streamlit-app.streamlit.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/company/", response_model=list[Company])
def read_company(skip: int = 0, limit: Optional[int] = None, db: Session = Depends(get_db)):
    company = crud.get_company(db, skip=skip, limit=limit)
    return company

@app.get("/headcount/", response_model=list[Headcount])
def read_headcount(skip: int = 0, limit: Optional[int] = None, db: Session = Depends(get_db)):
    headcount = crud.get_headcount(db, skip=skip, limit=limit)
    return headcount

@app.get("/revenue/", response_model=list[Revenue])
def read_revenue(skip: int = 0, limit: Optional[int] = None, db: Session = Depends(get_db)):
    revenue = crud.get_revenue(db, skip=skip, limit=limit)
    return revenue

@app.get("/date/", response_model=list[Dim_Date])
def read_date(skip: int = 0, limit: Optional[int] = None, db: Session = Depends(get_db)):
    date = crud.get_date(db, skip=skip, limit=limit)
    return date