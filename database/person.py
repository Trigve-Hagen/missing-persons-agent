# https://www.youtube.com/watch?v=AKQ3XEDI9Mw
# schema - person - person of interest - id, iid, ifMissing - missing or POI, ssn, gender, dob

from sqlalchemy import ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func
from database.base import Base

class Person(Base):
  __tablename__ = "people"

  id = Column("id", Integer, primary_key=True)
  firstName = Column("firstName", String)
  middleName = Column("middleName", String)
  lastName = Column("lastName", String)
  sirName = Column("sirName", String)
  ifMissing = Column("ifMissing", Boolean, default=True, nullable=False)
  linkedBy = Column("linkedBy", String) # what are they linked by service, contacts
  height = Column("height", String)
  weight = Column("weight", String)
  hairColor = Column("hairColor", String)
  eyeColor = Column("eyeColor", String)
  ssn = Column("ssn", Integer)
  gender = Column("gender", CHAR)
  dob = Column("dob", DateTime)

  def __init__(self, id, firstName, middleName, lastName, sirName, ifMissing, linkedBy, height, weight, hairColor, eyeColor, ssn, gender, dob):
    self.id = id
    self.ifMissing = ifMissing
    self.firstName = firstName
    self.middleName = middleName
    self.lastName = lastName
    self.sirName = sirName
    self.linkedBy = linkedBy
    self.height = height
    self.weight = weight
    self.hairColor = hairColor
    self.eyeColor = eyeColor
    self.ssn = ssn
    self.gender = gender
    self.dob = dob

  def __repr__(self):
    return f"({self.id}) {self.ifMissing} {self.firstName} {self.middleName} {self.lastName} {self.sirName} {self.linkedBy} {self.height} {self.weight} {self.hairColor} {self.eyeColor} {self.ssn} ({self.gender}, {self.dob})"

class Alias(Base):
  __tablename__ = "aliases"

  id = Column("id", Integer, primary_key=True)
  firstName = Column("firstName", String)
  middleName = Column("middleName", String)
  lastName = Column("lastName", String)
  sirName = Column("sirName", String)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, id, ifAlias, firstName, middleName, lastName, sirName, owner):
    self.id = id
    self.firstName = firstName
    self.middleName = middleName
    self.lastName = lastName
    self.sirName = sirName
    self.owner = owner

  def __repr__(self):
    return f"({self.id}){self.firstName} {self.middleName} {self.lastName} {self.sirName} owned by {self.owner}"

  def validate():
    pass

class Address(Base):
  __tablename__ = "addresses"

  id = Column("id", Integer, primary_key=True)
  ifCrimeScene = Column("ifCrimeScene", Boolean, default=False, nullable=False)
  type = Column(String(20)) # home, work
  name = Column("name", String) # name of business if work address
  address1 = Column("address1", String)
  address2 = Column("address2", String)
  city = Column("city", String)
  state = Column("state", String)
  zip5 = Column("zip5", Integer)
  zip4 = Column("zip4", Integer)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, id, ifCrimeScene, type, name, address1, address2, city, state, zip5, zip4, owner):
    self.id = id
    self.ifCrimeScene = ifCrimeScene
    self.type = type
    self.name = name
    self.address1 = address1
    self.address2 = address2
    self.city = city
    self.state = state
    self.zip5 = zip5
    self.zip4 = zip4
    self.owner = owner

  def __repr__(self):
    return f"({self.id}) {self.ifCrimeScene} {self.type} {self.name} {self.address1} {self.address2} {self.city} {self.state} {self.zip5} {self.zip4} owned by {self.owner}"

  def validate():
    pass

class Email(Base):
  __tablename__ = "emails"

  id = Column("id", Integer, primary_key=True)
  type = Column(String(20)) # personel, work
  email = Column(String(255), unique=True, nullable=False)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, id, type, email, owner):
    self.id = id
    self.type = type
    self.email = email
    self.owner = owner

  def __repr__(self):
    return f"({self.id}) {self.type} {self.email} owned by {self.owner}"

  def validate():
    pass

class Phone(Base):
  __tablename__ = "phones"

  id = Column("id", Integer, primary_key=True)
  type = Column(String(20)) # cell, home, work
  phone = Column(String(20), unique=True, nullable=False)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, id, type, phone, owner):
    self.id = id
    self.type = type
    self.phone = phone
    self.owner = owner

  def __repr__(self):
    return f"({self.id}) {self.type} {self.phone} owned by {self.owner}"

  def validate():
    pass

class PersonRepository:
  def __int__(self, person: Person, alias: Alias, email: Email, phone: Phone, address: Address):
    self.person = person
    self.alias = alias
    self.email = email
    self.phone = phone
    self.address = address
