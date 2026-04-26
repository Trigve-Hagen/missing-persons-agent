# schema - missing - caseid, etc.. - identifies the main person
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func
from base import Base # Import shared base

class Missing(Base):
  def __init__(self):
    pass
