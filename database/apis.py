# schema - apis - id, name, url, key, secret
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func
from database.base import Base, NullToEmptyString # Import shared base

class Api(Base):
  __tablename__ = "api"

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString)
  url = Column(NullToEmptyString)
  key = Column(NullToEmptyString)
  secret = Column(NullToEmptyString)
  description = Column(NullToEmptyString)

  def __init__(self, name, url, key, secret, description):
    self.name = name
    self.url = url
    self.key = key
    self.secret = secret
    self.description = description

class ApiField(Base):
  __tablename__ = "api_fields"

  id = Column("id", Integer, primary_key=True)
  field = Column(NullToEmptyString, unique=True, nullable=False)
  value = Column(NullToEmptyString)
  description = Column(NullToEmptyString)
  owner = Column(Integer, ForeignKey("api.id"))

  def __init__(self, field, value, description, owner):
    self.field = field
    self.value = value
    self.description = description
    self.owner = owner

