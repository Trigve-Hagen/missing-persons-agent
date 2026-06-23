from sqlalchemy import create_engine, ForeignKey, Column, JSON, String, Integer, CHAR, DateTime, Boolean, func
from database.base import Base, NullToEmptyString # Import shared base

class Api(Base):
  __tablename__ = "api"
  __table_args__ = {"comment": "This table stores the api information"}

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString, comment="The user generated string name of the api.")
  type = Column(NullToEmptyString, comment="The allowed values are api or rss.")
  url = Column(NullToEmptyString, comment="The url endpoint.")
  key = Column(NullToEmptyString, comment="Where an api needs authentication this can hold one of the two key combinations used.")
  secret = Column(NullToEmptyString, comment="Where an api needs authentication this can hold one of the two key combinations used.")
  description = Column(NullToEmptyString, comment="A description of the api.")

  def __init__(self, name, type, url, key, secret, description):
    self.name = name
    self.type = type
    self.url = url
    self.key = key
    self.secret = secret
    self.description = description

class ApiField(Base):
  __tablename__ = "api_fields"
  __table_args__ = {"comment": "This table stores the api fields passed as a query string for filtering."}

  id = Column("id", Integer, primary_key=True)
  field = Column(NullToEmptyString, comment="The field name in the query string or the tag name.")
  value = Column(NullToEmptyString, comment="The value in the query string or the classes delimited by a space.")
  type = Column(NullToEmptyString, comment="Describes the relationship of the classes for scraping. Allowed values are parent or child.")
  description = Column(NullToEmptyString, comment="A description of the api field.")
  owner = Column(Integer, ForeignKey("api.id"))

  def __init__(self, field, value, type, description, owner):
    self.field = field
    self.value = value
    self.type = type
    self.description = description
    self.owner = owner

class FeedLog(Base):
  """
  Captures metadata from ingested external feeds, public API webhooks, or scrapers.
  """

  __tablename__ = "feed_logs"
  __table_args__ = {"comment": "This table captures metadata from ingested external feeds, public API webhooks, or scrapers."}

  id = Column("id", Integer, primary_key=True)
  version = Column(Integer, comment="The version of the API or Feed payload.")
  source = Column(NullToEmptyString, comment="Origin name of the automated feed (e.g., 'Amityville-PD-RSS', 'Amber-Alert-API').")
  rawPayload = Column("raw_payload", JSON, nullable=False, comment="Raw json payload returned from the api request.")
  rawPayloadHash = Column("raw_payload_hash", NullToEmptyString, comment="Unique MD5/SHA256 string used to prevent duplicate system entry.")
  owner = Column(Integer, ForeignKey("api.id"))

  def __init__(self, version, source, rawPayload, rawPayloadHash, owner):
    self.version = version
    self.source = source
    self.rawPayload = rawPayload
    self.rawPayloadHash = rawPayloadHash
    self.owner = owner

