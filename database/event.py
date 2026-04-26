# schema - event - eventId, personId, date, time, description
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func
from database.base import Base # Import shared base

class Event(Base):
  __tablename__ = "events"

  eid = Column("eid", Integer, primary_key=True)
  eventType = Column("eventType", String)
  description = Column("description", String)
  owner = Column(Integer, ForeignKey("people.pid"))

  def __init__(self, eid, eventType, description, owner):
    self.eid = eid
    self.eventType = eventType
    self.description = description
    self.owner = owner

  def __repr__(self):
    return f"({self.eid}) {self.eventType} {self.description} owned by {self.owner}"

  def validate():
    pass
