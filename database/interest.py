# schema - interest - interestId, personId, type - email, phone, service, etc..,
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func
from base import Base # Import shared base

class Interest(Base):
  def __init__(self):
    pass
