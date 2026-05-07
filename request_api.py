from sqlalchemy import create_engine, inspect, exc, select, update
from database.state import State
from database.category import Category
from database.event import Event, Url, Question
from database.news import News
from database.apis import Api, ApiField
from database.person import Person, Alias, Email, Phone, Address
import requests

class RequestApi:
  def __init__(self, session):
    self.session = session
    self.params = {}
    self.state = self.session.execute(select(State).filter_by(id = 1)).scalar_one_or_none()
    self.api = session.execute(select(Api).filter_by(id = self.state.api)).scalar_one_or_none()
    self.apiFields = session.scalars(select(ApiField).filter_by(owner = self.api.id)).all()

  def get_api(self):
    return self.session.execute(select(Api).filter_by(id = self.state.api)).scalar_one_or_none()

  def get_params(self):
    # Search for a person by title
    for fields in self.apiFields:
      self.params[fields.field] = fields.value

  def get_api_params(self):
    self.get_params()
    return self.params

  def get_request(self):
    self.get_params()
    response = requests.get(self.api.url, params=self.params)

    if response.status_code == 200:
      data = response.json()
      # Access the first matching person
      return data
      # print(f"Name: {person['title']}")
      # print(f"Details: {person['description']}")
    else:
      return "Error."
