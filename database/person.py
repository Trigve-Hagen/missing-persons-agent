from sqlalchemy import ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func, Text
from database.base import Base, NullToEmptyString
from sqlalchemy.orm import relationship
from datetime import datetime

class Category(Base):
  """
  All categories organizing emails, addresses, phones etc. Anything that needs
  organization. You can create more.
  """

  __tablename__ = "categories"
  __table_args__ = {"comment": "This table stores the categories of Person, Email, Phone, Address and Event."}

  id = Column("id", Integer, primary_key=True)
  type = Column(NullToEmptyString(20), comment="The category type. Allowed values are: addressType, contactType, emailType, phoneType, eventType.")
  name = Column(NullToEmptyString(255), comment="The user generated string name of the category.")

  def __init__(self, type, name):
    self.type = type
    self.name = name

class Person(Base):
  """
  The person class holds just the description of the person but is the
  center point for adding all information about them into the investigation
  vector database.
  """

  __tablename__ = "people"
  __table_args__ = {"comment": "This table stores the people. Its mainly the descriptive properties. The only none descriptive property at this time is the SSN."}

  id = Column("id", Integer, primary_key=True)
  firstName = Column("first_name", NullToEmptyString, comment="The persons first name.")
  middleName = Column("middle_name", NullToEmptyString, comment="The persons middle name.")
  lastName = Column("last_name", NullToEmptyString, comment="The persons last name.")
  sirName = Column("sir_name", NullToEmptyString, comment="The persons sir name.")
  suffix = Column(NullToEmptyString, comment="The persons suffix name.")
  type = Column(Integer, ForeignKey('categories.id'), comment="The type of user. Types are defined in Category. There is an immutable Missing Person value. All other values can be added and changed by the user.")
  height = Column(Integer, comment="The height of the person.")
  weight = Column(Integer, comment="The weight of the person.")
  hairColor = Column("hair_color", NullToEmptyString, comment="The hair color of the person.")
  eyeColor = Column("eye_color", NullToEmptyString, comment="The height of the person.")
  ssn = Column(NullToEmptyString, comment="The persons SSN. This is used here to check if someone is trying to use there credit in a nefarious way.")
  gender = Column(NullToEmptyString, comment="The gender of the person. Allowed values are male and female.")
  dob = Column(DateTime, comment="The date of birth of the person.")
  ethnicity = Column(NullToEmptyString, comment="The ethnicity of the person.")
  primaryLanguage = Column("primary_language", NullToEmptyString, comment="The primary language of the person.")
  missing = Column(DateTime, comment="The date the missing person went missing or the date that the person of interest met the missing person.")
  description = Column(Text, comment="A place to add more descriptive information about the person.")
  owner = Column(Integer, default=0, comment="This will be 0 if a missing person(Level 1). If level 2 contacts then this will be the missing persons id. If level 3 then this will be the person of interests id that they knew. This can get crazy big in memory usage as you continue to level up etc..")
  # Relationships
  category = relationship(Category)
  emails = relationship("Email", backref="person")
  phones = relationship("Phone", backref="person")
  addresses = relationship("Address", backref="person")
  aliases = relationship("Alias", backref="person")

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
    s1, s2, s3, s4, s5 = self.sirName, self.firstName, self.middleName, self.lastName, self.suffix
    name = " ".join([s for s in [s1, s2, s3, s4, s5] if s])
    cat_name = self.category.name if self.category else "Unknown"
    age = str(datetime.now().year - self.dob.year) if self.dob else "Unknown"
    missing_date = self.missing.strftime("%B %d, %Y at %I:%M %p")

    aliases_list = ""
    for index, al in enumerate(self.aliases):
      s1, s2, s3, s4, s5 = al.sirName, al.firstName, al.middleName, al.lastName, al.suffix
      name = " ".join([s for s in [s1, s2, s3, s4, s5] if s])
      if index == 0:
        aliases_list = name
      else:
        aliases_list += ", "+name

    addresses_list = ""
    for index, ad in enumerate(self.addresses):
      s1, s2, s3, s4, s5 = ad.address1, ad.address2, ad.city, ad.state, ad.zip5
      name = " ".join([s for s in [s1, s2, s3, s4, str(s5)] if s])
      if index == 0:
        addresses_list = name
      else:
        addresses_list += ", "+name

    emails_list = ", ".join([e.email for e in self.emails]) if self.emails else "None"
    phones_list = ", ".join([p.phone for p in self.phones]) if self.phones else "None"

    gender = 'She'
    if self.gender == 'male':
      gender = 'He'

    missing_text = "has been a contact since"
    if cat_name == "Missing Person":
      missing_text = "went missing on"

    feet = (self.height // 12)
    inches = (self.height % 12)
    display_label = f"{feet}' {inches}\""

    # Start with an empty list
    chunks = []

    # Append strings
    chunks.append(
      f"Person: {name} is a {cat_name}. {gender} is {age} years old. {gender} {missing_text} {missing_date}. "
      f"Physical traits: {display_label} tall, {self.weight} lbs, {self.eyeColor} eyes, {self.hairColor} hair. "
      f"Ethnicity: {self.ethnicity}, primary language is {self.primaryLanguage}. "
    )
    if self.ssn != "" and self.ssn != 'None':
      chunks.append(f"Social Security Number: {self.ssn}. ")
    if self.description != "" and self.description != 'None':
      chunks.append(f"Other descriptive information: {self.description}. ")
    if emails_list != "" and emails_list != 'None':
      chunks.append(f"Contact emails: {emails_list}. ")
    if phones_list != "" and phones_list != 'None':
      chunks.append(f"Contact phones: {phones_list}. ")
    if addresses_list != "" and addresses_list != 'None':
      chunks.append(f"Addresses registered at: {addresses_list}. ")
    if aliases_list != "" and aliases_list != 'None':
      chunks.append(f"Known aliases for this person are: {aliases_list}. ")

    return " ".join(chunks)

class Alias(Base):
  """
  Aliases associated with the person.
  """

  __tablename__ = "aliases"
  __table_args__ = {"comment": "This table stores a persons aliases."}

  id = Column("id", Integer, primary_key=True)
  firstName = Column("first_name", NullToEmptyString, comment="The persons first name.")
  middleName = Column("middle_name", NullToEmptyString, comment="The persons middle name.")
  lastName = Column("last_name", NullToEmptyString, comment="The persons last name.")
  sirName = Column("sir_name", NullToEmptyString, comment="The persons sir name.")
  suffix = Column(NullToEmptyString, comment="The persons suffix name.")
  owner = Column(Integer, ForeignKey("people.id"), comment="The persons who uses this alias.")

  def __init__(self, firstName, middleName, lastName, sirName, suffix, owner):
    self.firstName = firstName
    self.middleName = middleName
    self.lastName = lastName
    self.sirName = sirName
    self.suffix = suffix
    self.owner = owner

class Address(Base):
  """
  Addresses associated with the person.
  """

  __tablename__ = "addresses"
  __table_args__ = {"comment": "This table stores a persons addresses."}

  id = Column("id", Integer, primary_key=True)
  type = Column(Integer, comment="The user defined type of address. Definitions are created in Category")
  name = Column(NullToEmptyString, comment="The user defined name of address.")
  address1 = Column("address_1", NullToEmptyString, comment="The address.")
  address2 = Column("address_2", NullToEmptyString, comment="The apartment number associated with the address.")
  city = Column(NullToEmptyString, comment="The city associated with the address.")
  state = Column(NullToEmptyString, comment="The state associated with the address.")
  zip5 = Column("zip_5", Integer, comment="The 5 digit zip code associated with the address.")
  zip4 = Column("zip_4", Integer, comment="The 4 digit zip code associated with the address.")
  owner = Column(Integer, ForeignKey("people.id"), comment="The persons who uses this address.")

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

class Email(Base):
  """
  Emails associated with the person.
  """

  __tablename__ = "emails"
  __table_args__ = {"comment": "This table stores a persons email addresses."}

  id = Column("id", Integer, primary_key=True)
  type = Column(Integer, comment="The user defined type of email. Definitions are created in Category")
  email = Column(NullToEmptyString(255), nullable=False, comment="The persons email address.")
  owner = Column(Integer, ForeignKey("people.id"), comment="The persons who uses this email.")

  def __init__(self, type, email, owner):
    self.type = type
    self.email = email
    self.owner = owner

class EmailMessage(Base):
  __tablename__ = "email_messages"
  __table_args__ = {"comment": "This table stores a emails sent and recieved from an email."}

  id = Column("id", Integer, primary_key=True)
  message = Column(Text)
  date = Column(DateTime)
  owner = Column(Integer, ForeignKey("emails.id"), comment="The email this email was made by.")

  def __init__(self, message, date, owner):
    self.message = message
    self.date = date
    self.owner = owner

class Phone(Base):
  """
  Phone numbers associated with the person.
  """

  __tablename__ = "phones"
  __table_args__ = {"comment": "This table stores a persons phone numbers."}

  id = Column("id", Integer, primary_key=True)
  type = Column(Integer, comment="The user defined type of phones. Definitions are created in Category")
  phone = Column(NullToEmptyString(20), nullable=False)
  owner = Column(Integer, ForeignKey("people.id"), comment="The persons who uses this phone number.")

  def __init__(self, type, phone, owner):
    self.type = type
    self.phone = phone
    self.owner = owner

class Call(Base):
  """
  Calls made from a Phone numbers.
  """

  __tablename__ = "calls"
  __table_args__ = {"comment": "This table stores a calls and texts sent and recieved from an phone number. Files will store audio files later."}

  id = Column("id", Integer, primary_key=True)
  type = Column(NullToEmptyString(20), comment="The type of call. The allowed values are text, call.")
  file = Column(Integer, comment="The file number if an audio file is associated with the call.")
  date = Column(DateTime, comment="The date the call was made.")
  owner = Column(Integer, ForeignKey("phones.id"), comment="The phone number the call or text was made by.")

  def __init__(self, file, date, owner):
    self.file = file
    self.date = date
    self.owner = owner

class File(Base):
  """
  Images, Documents, Audios(future) and Videos(future)
  all get added to the investigation vector database to be
  used in the investigation.
  """

  __tablename__ = 'files'
  __table_args__ = {"comment": "This table stores files like images, documents and later audio and videos associated with a person."}

  id = Column(Integer, primary_key=True)
  type = Column(NullToEmptyString, comment="The type of file. The allowed values are image, pdf for now.")
  filename = Column(NullToEmptyString, unique=True, nullable=False, comment="The file name.")
  owner = Column(Integer, ForeignKey("people.id"), comment="The persons file is associated with.")

  def __init__(self, type, filename, owner):
    self.type = type
    self.filename = filename
    self.owner = owner

class Event(Base):
  """
  Events related to the missing person
  that might hold weight in the investigation.
  """

  __tablename__ = "events"
  __table_args__ = {"comment": "This table stores events associated with persons. In the future they will be the base information for timelines."}

  id = Column("id", Integer, primary_key=True)
  type = Column(Integer, comment="The user defined type of Events. Definitions are created in Category")
  name = Column(NullToEmptyString) # name of business if work address
  description = Column(Text, comment="The event description.")
  dateFrom = Column("date_from", DateTime, comment="The start date of the event.")
  dateTo = Column("date_to", DateTime, comment="The end date of the event if there is one.")
  owner = Column(Integer, ForeignKey("people.id"), comment="The persons the event is associated with.")

  def __init__(self, type, name, description, dateFrom, dateTo, owner):
    self.type = type
    self.name = name
    self.description = description
    self.dateFrom = dateFrom
    self.dateTo = dateTo
    self.owner = owner

  def __repr__(self):
    dates = ""
    if self.dateTo != "" and self.dateTo != 'None':
      dates = f"Event Dates: from {self.dateFrom} to {self.dateTo}. "
    elif self.dateFrom != "" and self.dateFrom != 'None':
      dates = f"Event Date: on {self.dateFrom}. "

    return f"Event: {self.name} Event Details: {self.description} {dates}"

class Note(Base):
  """
  Notes related to the missing person
  that might hold weight in the investigation.
  """

  __tablename__ = "notes"
  __table_args__ = {"comment": "This table stores notes associated with persons."}

  id = Column("id", Integer, primary_key=True)
  name = Column(NullToEmptyString, comment="The name of the note.")
  note = Column(Text, comment="The note.")
  owner = Column(Integer, ForeignKey("people.id"), comment="The persons the note is associated with.")

  def __init__(self, name, note, owner):
    self.name = name
    self.note = note
    self.owner = owner

  def __repr__(self):
    return f"Note: {self.name} Note Details: {self.note} "
