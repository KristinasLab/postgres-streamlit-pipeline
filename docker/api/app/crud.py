# Contains functions that perform database operations
from sqlalchemy.orm import Session
from app.models import Company, Headcount, Revenue, Dim_Date
from typing import Optional

def get_company(postgres: Session, skip: int = 0, limit: Optional[int] = None):
    query = postgres.query(Company).offset(skip)
    if limit:
        query = query.limit(limit)
    return query.all()

def get_headcount(postgres: Session, skip: int = 0, limit: Optional[int] = None):
    query = postgres.query(Headcount).offset(skip)
    if limit:
        query = query.limit(limit)
    return query.all()

def get_revenue(postgres: Session, skip: int = 0, limit: Optional[int] = None):
    query = postgres.query(Revenue).offset(skip)
    if limit:
        query = query.limit(limit)
    return query.all()

def get_date(postgres: Session, skip: int = 0, limit: Optional[int] = None):
    query = postgres.query(Dim_Date).offset(skip)
    if limit:
        query = query.limit(limit)
    return query.all()