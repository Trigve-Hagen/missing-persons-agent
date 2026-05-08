from sqlalchemy import create_engine, inspect, exc, select, update
from database.state import State
from database.category import Category
from database.event import Event, Url, Question
from database.news import News
from database.apis import Api, ApiField
from database.person import Person, Alias, Email, Phone, Address

class Resources():
  def __init__(self, session):
    self.session = session

  def files_size(self):
    return "Be here soon.."

  def initial_database(self):
    return "Be here soon.."

  def eav_database(self):
    return "Be here soon.."

  def vector_database(self):
    return "Be here soon.."

  def ollama_models(self):
    return "Be here soon.."
