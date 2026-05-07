import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from flask import flash
from sqlalchemy import create_engine, inspect, exc, select, update
from database.state import State
from database.category import Category
from database.event import Event, Url, Question
from database.news import News
from database.apis import Api, ApiField
from database.person import Person, Alias, Email, Phone, Address

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

    try:
      # 1. Perform the request (always set a timeout to prevent hanging)
      response = requests.get(self.api.url, params=self.params, timeout=10)

      # 2. Raise an exception for 4xx or 5xx status codes
      response.raise_for_status()

      # 3. Process the response if no exception was raised
      data = response.json()

    except HTTPError as http_err:
        flash(f"HTTP error occurred: {http_err}", "danger")
        return "Http error. Please check that you are using correct api and field values."
    except ConnectionError as conn_err:
        flash(f"Connection error occurred: {conn_err}", "danger")
        return "Connection Error. Please check that you are using correct api and field values."
    except Timeout as timeout_err:
        flash(f"The request timed out: {timeout_err}", "danger")
        return "Request Timeout. Please check that you are using correct api and field values."
    except RequestException as req_err:
        flash(f"A general Requests error occurred: {req_err}", "danger")
        return "Request Exception. Please check that you are using correct api and field values."
    except Exception as e:
        flash(f"An unexpected non-requests error occurred: {e}", "danger")
        return "Exception. Request failed. Please check that you are using correct api and field values."
    else:
        flash("Success! Data retrieved.", "success")
        return data
