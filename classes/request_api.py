import ast
import json
import requests
import feedparser
from jsonpath_ng import parse
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from flask import flash

class RequestApi:

  def if_list(node):
    if isinstance(node, list):
      if len(node) == 0:
        return True # "Empty list: []"
      elif all(isinstance(item, dict) for item in node):
        return True # "List of dictionaries: [{'name': 'value'}]"
      else:
        return False # "List of other types"

  def format_node_to_csv(node):
    # 1. Check if it's already a string
    if isinstance(node, str):
      return node

    # 2. Check if it's a list (one or more values)
    if isinstance(node, list):
      if not node:
        return ""

      formatted_items = []
      for item in node:
        # 3. Check for name-value pattern like [{"name": "value"}]
        if isinstance(item, dict) and 'name' in item:
          formatted_items.append(str(item['name']))
        else:
          # Handle standard list of values
          formatted_items.append(str(item))

      # Return comma separated string
      return ", ".join(formatted_items)

    # Fallback for other types
    return str(node)

  def filter_data(self, data, state):
    if state.root_node:
      filter = '$.'+state.root_node
      try:
        if parse(filter).find(data):
          return parse(filter).find(data)[0].value
      except Exception as e:
        flash(f"An unexpected error occurred: {e}", "danger")
    return data

  def get_request(self, api, apiFields):
    params = {}
    for fields in apiFields:
      params[fields.field] = fields.value

    try:
      # 1. Perform the request (always set a timeout to prevent hanging)
      response = requests.get(api.url, params=params, timeout=10)

      # 2. Raise an exception for 4xx or 5xx status codes
      response.raise_for_status()

      if api.type == 'api':
        # 3. Process the response if no exception was raised
        data = response.json()

        return data

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
      flash(f"The unexpected non-requests error occurred because the api needs to be set in order to make the request so it errors.", "info")
      return "Exception. Request failed. Please check that you are using correct api and field values."
    else:
      data = []
      if api.type == 'rss':
        # Parse the content with feedparser
        data = feedparser.parse(response.content)
        if data.bozo:
          flash(f"Warning: Non-well-formed feed: {data.bozo_exception}", "warning")
          # return "Warning. Non-well-formed feed. Please check that you are using correct api and field values."

        flash("Success! Data retrieved.", "success")

      return data
