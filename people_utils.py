from sqlalchemy import create_engine, inspect, exc, select, update
from database.state import State
from database.category import Category
from database.event import Event, Url, Question
from database.news import News
from database.apis import Api, ApiField
from database.person import Person, Alias, Email, Phone, Address

def object_as_dict(obj):
  return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

class PeopleUtils:
  def __init__(self, session):
    self.session = session
    self.state = self.session.execute(select(State).filter_by(id =1)).scalar_one_or_none()

  def get_height_options(self):
    height_options = []
    for feet in range(4, 8):  # From 4ft to 7ft
      for inches in range(12):
          if feet == 7 and inches > 0: # Cap at exactly 7'0"
              break
          total_inches = (feet * 12) + inches
          display_label = f"{feet}' {inches}\""
          height_options.append((total_inches, display_label))
    return height_options

  def people_params(self):
    stmt = select(Category).where(Category.type == "contactType")
    contactType_select = self.session.execute(stmt).scalars().all()
    hair_color_codes = [
      ("BLK", "Black"),
      ("BLN", "Blond"),
      ("BRN", "Brown"),
      ("DBR", "Dark Brown"),
      ("LBR", "Light Brown"),
      ("RED", "Red or Auburn"),
      ("GRY", "Gray"),
      ("WHI", "White"),
      ("XXX", "Unknown/Bald")
    ]
    eye_colors = ["Brown", "Blue", "Hazel", "Green", "Grey", "Amber", "Other"]

    return contactType_select, hair_color_codes, eye_colors

  def name_params(self):
    name_suffixes = ["Jr.", "Sr.", "II", "III", "IV", "V", "MD", "PhD", "JD", "DDS"]
    sir_names = ["Mr.", "Mrs.", "Miss."]
    return sir_names, name_suffixes

  def get_person(self):
    return self.session.execute(select(Person).filter_by(id = self.state.person)).scalar_one_or_none()

  def get_all_person(self):
    person = self.session.execute(select(Person).filter_by(id = self.state.person)).scalar_one_or_none()
    alias_stmt = select(Alias).where(Alias.owner == self.state.person)
    aliases = self.session.execute(alias_stmt).scalars().all()
    phone_stmt = select(Phone).where(Phone.owner == self.state.person)
    phones = self.session.execute(phone_stmt).scalars().all()
    address_stmt = select(Address).where(Address.owner == self.state.person)
    addresses = self.session.execute(address_stmt).scalars().all()
    email_stmt = select(Email).where(Email.owner == self.state.person)
    emails = self.session.execute(email_stmt).scalars().all()
    return person, aliases, addresses, emails, phones

  def get_person_name(self, person):
    s1, s2, s3, s4, s5 = person.sirName, person.firstName, person.middleName, person.lastName, person.suffix
    return " ".join([s for s in [s1, s2, s3, s4, s5] if s])

class ValueOptions:
  def __init__(self, session):
    self.session = session
    self.options = {}
    people_utils = PeopleUtils(session=self.session)
    person = people_utils.get_person()
    self.options["person_name"] = people_utils.get_person_name(person)

  def get_value_options(self):
    return self.options

  def get_options_value(self, value):
    return self.options[value]

