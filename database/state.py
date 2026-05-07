# schema - apis - id, name, url, key, secret
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func, CheckConstraint
from database.base import Base, NullToEmptyString # Import shared base

class State(Base):
  __tablename__ = 'state'
  __table_args__ = (
    CheckConstraint('id = 1', name='only_one_row'),
  )

  id = Column(Integer, primary_key=True, default=1)
  person = Column(Integer, default=0)
  api = Column(Integer, default=0)
