from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class Company(BaseModel):
    company_id: int
    company_name: str
    location: str
    industry: str

    class Config:
        from_attributes = True  # correct if you're using Pydantic v2
        # For Pydantic v1.x, use: orm_mode = True
        
class Headcount(BaseModel):
    id: int
    company_id: int
    month: date
    employee_count: int

    class Config:
        from_attributes = True 

class Revenue(BaseModel):
    id: int
    company_id: int
    month: date
    revenue_eur: int

    class Config:
        from_attributes = True  
        
class Dim_Date(BaseModel):
    month_id: int
    month_num: int
    year: int
    quarter: int
    month_name: str
    month: date

    class Config:
        from_attributes = True  
