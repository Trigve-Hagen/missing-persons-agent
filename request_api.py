import requests
import feedparser
from jsonpath_ng import parse
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from flask import flash

class RequestApi:

  def filter_data(self, data, state):
    if state.root_node:
      filter = '$.'+state.root_node
      if parse(filter).find(data):
        return parse(filter).find(data)[0].value, True
    return data, False

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
        if api.type == 'rss':
          # Parse the content with feedparser
          data = feedparser.parse(response.content)
          if data.bozo:
            flash(f"Warning: Non-well-formed feed: {data.bozo_exception}", "warning")
            # return "Warning. Non-well-formed feed. Please check that you are using correct api and field values."

        flash("Success! Data retrieved.", "success")
        return data
