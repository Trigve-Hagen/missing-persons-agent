# pip install flask Flask-SQLAlchemy pandas numpy scikit-learn tensorflow
from data import Data
from config import Config
import flask
from flask import Flask, request, session, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
import os
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app=Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_very_secret_key_here'

db = SQLAlchemy(app)
class CompetitionSettings(db.Model):
  __tablename__ = 'missing_persons'
  id = db.Column(db.Integer, primary_key=True, default=1)
  competition = db.Column(db.String(100), default='march_madness')
  submission = db.Column(db.String(100), default='initial')

def initialize_settings():
  with app.app_context():
    # Create tables if they don't exist
    db.create_all()

    # Check if the single row exists
    settings = db.session.get(CompetitionSettings, 1)
    if settings is None:
      # If not, create it
      initial_settings = CompetitionSettings(id=1)
      db.session.add(initial_settings)
      db.session.commit()

def update_row(column, value):
  settings = db.session.get(CompetitionSettings, 1)
  if settings:
    if column == 'competition':
      settings.competition = value
    else:
      settings.submission = value

    db.session.commit()

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

if __name__ == '__main__':
  initialize_settings()
  app.run(debug=True)
