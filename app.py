# pip install flask Flask-SQLAlchemy sqlalchemy-utils
import os
import flask
from config import Config
from flask import Flask, request, session, jsonify, current_app
from sqlalchemy import create_engine, inspect
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from database.base import Base
from database.event import Event, Url, Question
from database.news import News
from database.person import Person, Alias, Email, Phone, Address

import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

script_dir = Path(__file__).parent
DATABASE = script_dir / "database" / "db" / "hope.db"

app=Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_very_secret_key_here'

@app.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')

@app.after_request
def add_nosniff_header_to_static(response):
    # Check if the request path starts with the static files URL
    if request.path.startswith(app.static_url_path):
        response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.route('/')
@app.route('/index')
def index():
  return flask.render_template('index.html')

@app.route('/data')
def data():
  return flask.render_template('data.html')

engine = create_engine(f"sqlite:///{DATABASE}", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def initialize_database(engine):
  if not database_exists(engine.url):
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
  initialize_database(engine)
  app.run(debug=True)

# python -m venv .venv
# .\.venv\Scripts\Activate.ps1
# python app.py
