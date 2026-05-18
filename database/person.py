from sqlalchemy import ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func, Text
from database.base import Base, NullToEmptyString
from sqlalchemy.orm import relationship
from datetime import datetime

# All categories organizing emails, addresses, phones etc. Anything that needs
# organization. You can create more.
class Category(Base):
  __tablename__ = "categories"

  id = Column("id", Integer, primary_key=True)
  type = Column(NullToEmptyString(20)) # contactType
  name = Column(NullToEmptyString(255))

  def __init__(self, type, name):
    self.type = type
    self.name = name

# The person class holds just the description of the person but is the
# center point for adding all information about them into the investigation
# vector database.
class Person(Base):
  __tablename__ = "people"

  id = Column("id", Integer, primary_key=True)
  firstName = Column("first_name", NullToEmptyString)
  middleName = Column("middle_name", NullToEmptyString)
  lastName = Column("last_name", NullToEmptyString)
  sirName = Column("sir_name", NullToEmptyString)
  suffix = Column(NullToEmptyString)
  type = Column(Integer, ForeignKey('categories.id'))
  height = Column(Integer)
  weight = Column(Integer)
  hairColor = Column("hair_color", NullToEmptyString)
  eyeColor = Column("eye_color", NullToEmptyString)
  ssn = Column(NullToEmptyString)
  gender = Column(NullToEmptyString)
  dob = Column(DateTime)
  ethnicity = Column(NullToEmptyString)
  primaryLanguage = Column("primary_language", NullToEmptyString)
  missing = Column(DateTime)
  description = Column(Text)
  owner = Column(Integer, default=0)
  # Relationships
  category = relationship(Category)
  emails = relationship("Email", backref="person")
  phones = relationship("Phone", backref="person")
  addresses = relationship("Address", backref="person")
  aliases = relationship("Alias", backref="person")
  events = relationship("Event", backref="person")
  notes = relationship("Note", backref="person")

  def __init__(self, firstName, middleName, lastName, sirName, suffix, type, height, weight, hairColor, eyeColor, ssn, gender, dob, ethnicity, primaryLanguage, missing, description, owner):
    self.firstName = firstName
    self.middleName = middleName
    self.lastName = lastName
    self.sirName = sirName
    self.suffix = suffix
    self.type = type
    self.height = height
    self.weight = weight
    self.hairColor = hairColor
    self.eyeColor = eyeColor
    self.ssn = ssn
    self.gender = gender
    self.dob = dob
    self.ethnicity = ethnicity
    self.primaryLanguage = primaryLanguage
    self.missing = missing
    self.description = description
    self.owner = owner

  def __repr__(self):
    # 1. Fetch related data and handle None values
    cat_name = self.category.name if self.category else "Unknown"
    age = str(datetime.now().year - self.dob.year) if self.dob else "Unknown"
    missing_date = self.missing.strftime("%B %d, %Y at %I:%M %p")

    emails_list = ", ".join([e.email for e in self.emails]) if self.emails else "None"
    phones_list = ", ".join([p.phone for p in self.phones]) if self.phones else "None"
    addresses_list = ", ".join([a.address for a in self.addresses]) if self.addresses else "None"
    aliases_list = ", ".join([al.alias for al in self.aliases]) if self.aliases else "None"
    events_list = ", ".join([al.alias for al in self.events]) if self.events else "None"
    notes_list = ", ".join([al.alias for al in self.notes]) if self.notes else "None"

    s1, s2, s3, s4, s5 = self.sirName, self.firstName, self.middleName, self.lastName, self.suffix
    name = " ".join([s for s in [s1, s2, s3, s4, s5] if s])

    gender = 'She'
    if self.gender == 'male':
      gender = 'He'

    missing_text = "has been a contact since"
    if cat_name == "Missing Person":
      missing_text = "went missing on"

    # 2. Build the sentence chunk
    chunk = (
      f"Person: {name} is a {cat_name}. {gender} is {age} years old. {gender} {missing_text} {missing_date}. {self.description}. "
      f"Physical traits: {self.height} tall, {self.weight} weight, {self.eyeColor} eyes, {self.hairColor} hair. "
      f"Ethnicity: of {self.ethnicity} decent, primary language is {self.primaryLanguage}. "
      f"Contact information includes emails: {emails_list}, and phones: {phones_list}. "
      f"Addresses are registered at: {addresses_list}. "
      f"Known aliases for this person are: {aliases_list}."
      f"Events for this person are: {events_list}."
      f"Notes for this person are: {notes_list}."
    )
    return chunk

# Aliases associated with the person.
class Alias(Base):
  __tablename__ = "aliases"

  id = Column("id", Integer, primary_key=True)
  firstName = Column("first_name", NullToEmptyString)
  middleName = Column("middle_name", NullToEmptyString)
  lastName = Column("last_name", NullToEmptyString)
  sirName = Column("sir_name", NullToEmptyString)
  suffix = Column(NullToEmptyString)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, firstName, middleName, lastName, sirName, suffix, owner):
    self.firstName = firstName
    self.middleName = middleName
    self.lastName = lastName
    self.sirName = sirName
    self.suffix = suffix
    self.owner = owner

# Addresses associated with the person.
class Address(Base):
  __tablename__ = "addresses"

  id = Column("id", Integer, primary_key=True)
  type = Column(Integer) # home, work
  name = Column(NullToEmptyString) # name of business if work address
  address1 = Column("address_1", NullToEmptyString)
  address2 = Column("address_2", NullToEmptyString)
  city = Column(NullToEmptyString)
  state = Column(NullToEmptyString)
  zip5 = Column("zip_5", Integer)
  zip4 = Column("zip_4", Integer)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, type, name, address1, address2, city, state, zip5, zip4, owner):
    self.type = type
    self.name = name
    self.address1 = address1
    self.address2 = address2
    self.city = city
    self.state = state
    self.zip5 = zip5
    self.zip4 = zip4
    self.owner = owner

# Emails associated with the person.
class Email(Base):
  __tablename__ = "emails"

  id = Column("id", Integer, primary_key=True)
  type = Column(Integer) # personel, work
  email = Column(NullToEmptyString(255), nullable=False)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, type, email, owner):
    self.type = type
    self.email = email
    self.owner = owner

# Phone numbers associated with the person.
class Phone(Base):
  __tablename__ = "phones"

  id = Column("id", Integer, primary_key=True)
  type = Column(Integer) # cell, home, work
  phone = Column(NullToEmptyString(20), nullable=False)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, type, phone, owner):
    self.type = type
    self.phone = phone
    self.owner = owner

# Images, PDFs, Excels, Word, Videos
# All get added to the investigation vector database to be
# used in the investigation.
class File(Base):
  __tablename__ = 'files'

  id = Column(Integer, primary_key=True)
  type = Column(Integer)
  filename = Column(NullToEmptyString, unique=True, nullable=False)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, type, filename, owner):
    self.type = type
    self.filename = filename
    self.owner = owner

# Events related to the missing person
# that might hold weight in the investigation.
class Event(Base):
  __tablename__ = "events"

  id = Column("id", Integer, primary_key=True)
  type = Column(Integer) # cell, home, work
  name = Column(NullToEmptyString) # name of business if work address
  description = Column(Text)
  dateFrom = Column("date_from", DateTime)
  dateTo = Column("date_to", DateTime)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, type, name, description, dateFrom, dateTo, owner):
    self.type = type
    self.name = name
    self.description = description
    self.dateFrom = dateFrom
    self.dateTo = dateTo
    self.owner = owner

# Notes related to the missing person
# that might hold weight in the investigation.
class Note(Base):
  __tablename__ = "notes"

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString) # name of business if work address
  note = Column(Text)
  owner = Column(Integer, ForeignKey("people.id"))

  def __init__(self, name, note, owner):
    self.name = name
    self.note = note
    self.owner = owner
