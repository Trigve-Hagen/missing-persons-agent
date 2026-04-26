# schema - event - eventId, personId, date, time, description
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func
from base import Base # Import shared base

class Event(Base):
  def __init__(self):
    pass
