from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base

class Company(Base):
    __tablename__ = 'dim_company'

    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True, nullable=False)
    location = Column(String, nullable=True)
    industry = Column(String, nullable=True)

class Dim_Date(Base):
    __tablename__ = 'dim_date'

    month_id = Column(Integer, primary_key=True, index=True)
    month_num = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month_name = Column(String, nullable=False)
    month = Column(Date, unique=True, nullable=False)
    
class Revenue(Base):
    __tablename__ = 'fact_revenue'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    month = Column(Date, nullable=False)
    revenue_eur = Column(Float, nullable=False)
    
class Headcount(Base):
    __tablename__ = 'fact_headcount'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, nullable=False)
    month = Column(Date, nullable=False)
    employee_count = Column(Integer, nullable=False)