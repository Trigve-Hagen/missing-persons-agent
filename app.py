# pip install flask Flask-SQLAlchemy sqlalchemy-utils
import os
import flask
from config import Config
from flask import Flask, request, session, current_app, redirect, flash, render_template, url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, inspect, exc, select
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
from database.base import Base
from database.category import Category
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

@app.route('/category')
def category():
  all_categories = session.query(Category).all()
  return flask.render_template('category.html', categories=all_categories)

@app.route('/set_category', methods=['POST'])
def set_category():
  form_data = request.form
  try:
    new_entry = Category(
      type=form_data.get('type'),
      name=form_data.get('name')
    )
    session.add(new_entry)
    session.commit()
    flash("Category added successfully!", "success")
    return redirect(url_for('category'))
  except IntegrityError as e:
    session.rollback()  # Always rollback on error to reset the session
    error_msg = str(e.orig) # Gets the specific database error message
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('category'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('category'))

@app.route('/person')
def person():
  missing_exists = session.query(
    session.query(Person).filter_by(ifMissing=True).exists()
  ).scalar()

  stmt = select(Category).where(Category.type == "contactType")
  contactType_select = session.execute(stmt).scalars().all()

  height_options = []
  for feet in range(4, 8):  # From 4ft to 7ft
    for inches in range(12):
        if feet == 7 and inches > 0: # Cap at exactly 7'0"
            break
        total_inches = (feet * 12) + inches
        display_label = f"{feet}' {inches}\""
        height_options.append((total_inches, display_label))

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

  name_suffixes = ["Jr.", "Sr.", "II", "III", "IV", "V", "MD", "PhD", "JD", "DDS"]

  all_people = session.query(Person).all()
  all_aliases = session.query(Alias).all()
  all_addresses = session.query(Address).all()
  all_emails = session.query(Email).all()
  all_phones = session.query(Phone).all()
  return flask.render_template('person.html', missing_exists=missing_exists, height_options=height_options, weight_options=range(10, 401), hair_color_codes=hair_color_codes, eye_colors=eye_colors, suffixes=name_suffixes, people=all_people, aliases=all_aliases, addresses=all_addresses, emails=all_emails, phones=all_phones, contactTypes=contactType_select)

@app.route('/set_person', methods=['POST'])
def set_person():
  form_data = request.form
  try:
    formatted_date = datetime.strptime(form_data.get('dob'), '%Y-%m-%d')
    new_entry = Person(
      firstName=form_data.get('firstName'),
      middleName=form_data.get('middleName'),
      lastName=form_data.get('lastName'),
      sirName=form_data.get('sirName'),
      suffix=form_data.get('suffix'),
      ifMissing=form_data.get('ifMissing') == "True",
      contactType=form_data.get('contactType'),
      height=form_data.get('height'),
      weight=form_data.get('weight'),
      hairColor=form_data.get('hairColor'),
      eyeColor=form_data.get('eyeColor'),
      ssn=form_data.get('ssn'),
      gender=form_data.get('gender'),
      dob=formatted_date
    )
    session.add(new_entry)
    session.commit()
    flash("Person added successfully!", "success")
    return redirect(url_for('person'))
  except IntegrityError as e:
    session.rollback()  # Always rollback on error to reset the session
    error_msg = str(e.orig) # Gets the specific database error message
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('person'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('person'))

@app.route('/set_alias', methods=['POST'])
def set_alias():
  form_data = request.form
  try:
    new_entry = Alias(
      firstName=form_data.get('firstName'),
      middleName=form_data.get('middleName'),
      lastName=form_data.get('lastName'),
      sirName=form_data.get('sirName'),
      suffix=form_data.get('suffix'),
      owner=form_data.get('owner'),
    )
    session.add(new_entry)
    session.commit()
    flash("Alias added successfully!", "success")
    return redirect(url_for('person'))
  except IntegrityError as e:
    session.rollback()  # Always rollback on error to reset the session
    error_msg = str(e.orig) # Gets the specific database error message
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('person'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('person'))


engine = create_engine(f"sqlite:///{DATABASE}", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def initialize_database(engine):
  if not database_exists(engine.url):
    Base.metadata.create_all(bind=engine)

  if session.query(Category).first() is None:
    c1 = Category("contactType", "Missing Person")
    # c2 = Category("contactType", "Missing Person")
    # c3 = Category("contactType", "Missing Person")
    session.add(c1)
    # session.add(c2)
    # session.add(c3)
    session.commit()

if __name__ == '__main__':
  initialize_database(engine)
  app.run(debug=True)

# python -m venv .venv
# .\.venv\Scripts\Activate.ps1
# python app.py
