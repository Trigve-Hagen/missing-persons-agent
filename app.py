# ---...---...---...---...---...---...---...---...---...---...---...---...---
#
#                    HOW TO BUILD THIS APPLICATION
#
# 1. SETUP & INSTALLATION:
#    Open your terminal or command prompt and install the necessary libraries.
#
#    pip install pywebview
#    pip install pyinstaller
#
# 2. FILE STRUCTURE:
#    Make sure this Python script (e.g., app.py) is in the SAME folder as your
#    web files:
#    - index.html
#    - style.css
#    - script.js
#
# 3. CREATE THE .EXE FILE:
#    Navigate to your project folder in the terminal and run the following
#    command. This command bundles everything into a single executable file.
#
#    pyinstaller --onefile --windowed --add-data "index.html:." --add-data "style.css:." --add-data "script.js:." app.py
#
#    COMMAND BREAKDOWN:
#    --onefile   : Creates a single .exe file.
#    --windowed  : Hides the black command prompt window when your app runs.
#    --add-data  : Includes your web files in the application bundle.
#    app.py      : The name of this Python script.
#
# 4. RUN YOUR APPLICATION:
#    After the command finishes, look inside the newly created 'dist' folder.
#    You will find your 'app.exe' file there. You can now run it.
#
# ---...---...---...---...---...---...---...---...---...---...---...---...---

# pip install flask Flask-SQLAlchemy sqlalchemy-utils pythonnet pywin32 comtypes
import flask
import webview
import requests
import json
import os
import sys
from config import Config
from flask import Flask, request, session, current_app, redirect, flash, render_template, url_for, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, inspect, exc, select, update
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database.base import Base
from database.state import State
from database.category import Category
from database.event import Event, Url, Question
from database.news import News
from database.apis import Api, ApiField
from database.person import Person, Alias, Email, Phone, Address
from request_api import RequestApi
from people_utils import PeopleUtils, ValueOptions

import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

def resource_path(relative_path):
  """ Get absolute path to resource, works for dev and for PyInstaller """
  try:
      # PyInstaller creates a temp folder and stores path in _MEIPASS
      base_path = sys._MEIPASS
  except Exception:
      base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)
DATABASE = resource_path('database/db/database.db')

template_folder = resource_path('templates')
static_folder = resource_path('assets')
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.config.from_object(Config)
app.secret_key = 'your_very_secret_key_here'

@app.route('/favicon.ico')
def favicon():
  return current_app.send_static_file('favicon.ico')

@app.after_request
def add_nosniff_header_to_static(response):
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

  category_types = [
    ('addressType', 'Address Type'),
    ('contactType', 'Contact Type'),
    ('emailType', 'Email Type'),
    ('phoneType', 'Phone Type')
  ]
  return flask.render_template('category.html', categories=all_categories, category_types=category_types)

@app.route('/edit/category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
  # Retrieve category or return 404
  category = session.get(Category, id)
  if not category:
    return redirect(url_for('category'))

  category_types = [
    ('addressType', 'Address Type'),
    ('contactType', 'Contact Type'),
    ('emailType', 'Email Type'),
    ('phoneType', 'Phone Type')
  ]
  category_data = {
      'id': category.id,
      'type': category.type,
      'name': category.name
  }
  return flask.render_template('edit_category.html', category_data=category_data, category_types=category_types)

@app.route('/set_category', methods=['POST'])
def set_category():
  form_data = request.form
  try:
    catagory = session.execute(select(Category).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if catagory:
      uporadd = "updated"
      catagory.type=form_data.get('type')
      catagory.name=form_data.get('name')
    else:
      uporadd = "added"
      catagory = Category(
        type=form_data.get('type'),
        name=form_data.get('name')
      )
    session.merge(catagory)
    session.commit()
    flash("Category "+uporadd+" successfully!", "success")
    return redirect(url_for('category'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('category'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('category'))

@app.route('/person')
def person():
  stmt = select(Person, Category.name).join(Category, Person.type == Category.id)
  all_people = session.execute(stmt).all()
  people_utils = PeopleUtils(session=session)
  height_options = people_utils.get_height_options()
  contactType_select, hair_color_codes, eye_colors = people_utils.people_params()
  sir_names, name_suffixes = people_utils.name_params()

  return flask.render_template('person.html', people=all_people, contactTypes=contactType_select, height_options=height_options, weight_options=range(10, 401), hair_color_codes=hair_color_codes, eye_colors=eye_colors, suffixes=name_suffixes, sir_names=sir_names)

@app.route('/edit/person/<int:id>', methods=['GET', 'POST'])
def edit_person(id):
  # Retrieve person or return 404
  person = session.get(Person, id)
  if not person:
    return redirect(url_for('person'))

  people_utils = PeopleUtils(session=session)
  height_options = people_utils.get_height_options()
  contactType_select, hair_color_codes, eye_colors = people_utils.people_params()
  sir_names, name_suffixes = people_utils.name_params()

  # Serialize to JSON (assuming basic dictionary serialization)
  person_data = {
      'id': person.id,
      'firstName': person.firstName,
      'middleName': person.middleName,
      'lastName': person.lastName,
      'sirName': person.sirName,
      'suffix': person.suffix,
      'type': person.type,
      'height': person.height,
      'weight': person.weight,
      'hairColor': person.hairColor,
      'eyeColor': person.eyeColor,
      'ssn': person.ssn,
      'gender': person.gender,
      'dob': person.dob.strftime('%Y-%m-%d'),
  }
  return flask.render_template('edit_person.html', contactTypes=contactType_select, height_options=height_options, weight_options=range(10, 401), hair_color_codes=hair_color_codes, eye_colors=eye_colors, suffixes=name_suffixes, sir_names=sir_names, person_data=person_data)

@app.route('/set_person', methods=['POST'])
def set_person():
  form_data = request.form
  try:
    user = session.execute(select(Person).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    formatted_date = datetime.strptime(form_data.get('dob'), '%Y-%m-%d')
    if user:
      uporadd = "updated"
      user.firstName=form_data.get('firstName')
      user.middleName=form_data.get('middleName')
      user.lastName=form_data.get('lastName')
      user.sirName=form_data.get('sirName')
      user.suffix=form_data.get('suffix')
      user.type=form_data.get('type')
      user.height=form_data.get('height')
      user.weight=form_data.get('weight')
      user.hairColor=form_data.get('hairColor')
      user.eyeColor=form_data.get('eyeColor')
      user.ssn=form_data.get('ssn')
      user.gender=form_data.get('gender')
      user.dob=formatted_date
    else:
      uporadd = "added"
      user = Person(
        firstName=form_data.get('firstName'),
        middleName=form_data.get('middleName'),
        lastName=form_data.get('lastName'),
        sirName=form_data.get('sirName'),
        suffix=form_data.get('suffix'),
        type=form_data.get('type'),
        height=form_data.get('height'),
        weight=form_data.get('weight'),
        hairColor=form_data.get('hairColor'),
        eyeColor=form_data.get('eyeColor'),
        ssn=form_data.get('ssn'),
        gender=form_data.get('gender'),
        dob=formatted_date
      )

    session.merge(user)
    session.commit()
    flash("Person "+uporadd+" successfully!", "success")
    return redirect(url_for('person'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('person'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('person'))

@app.route('/alias')
def alias():
  all_aliases = session.query(Alias).all()
  owner_select = session.query(Person).all()
  people_utils = PeopleUtils(session=session)
  sir_names, name_suffixes = people_utils.name_params()

  return flask.render_template('alias.html', aliases=all_aliases, suffixes=name_suffixes, sir_names=sir_names, owners=owner_select)

@app.route('/edit/alias/<int:id>', methods=['GET', 'POST'])
def edit_alias(id):
    # Retrieve alias or return 404
    alias = session.get(Alias, id)
    if not alias:
      return redirect(url_for('alias'))

    # Serialize to JSON (assuming basic dictionary serialization)
    alias_data = {
        'id': alias.id,
        'firstName': alias.firstName,
        'middleName': alias.middleName,
        'lastName': alias.lastName,
        'sirName': alias.sirName,
        'suffix': alias.suffix,
        'owner': alias.owner
    }
    people_utils = PeopleUtils(session=session)
    sir_names, name_suffixes = people_utils.name_params()
    owner_select = session.query(Person).all()

    return flask.render_template('edit_alias.html', alias_data=alias_data, suffixes=name_suffixes, sir_names=sir_names, owners=owner_select)

@app.route('/set_alias', methods=['POST'])
def set_alias():
  form_data = request.form
  try:
    alias = session.execute(select(Alias).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if alias:
      uporadd = "updated"
      alias.firstName=form_data.get('firstName')
      alias.middleName=form_data.get('middleName')
      alias.lastName=form_data.get('lastName')
      alias.sirName=form_data.get('sirName')
      alias.suffix=form_data.get('suffix')
      alias.owner=form_data.get('owner')
    else:
      uporadd = "aadded"
      alias = Alias(
        firstName=form_data.get('firstName'),
        middleName=form_data.get('middleName'),
        lastName=form_data.get('lastName'),
        sirName=form_data.get('sirName'),
        suffix=form_data.get('suffix'),
        owner=form_data.get('owner'),
      )
    session.merge(alias)
    session.commit()
    flash("Alias "+uporadd+" successfully!", "success")
    return redirect(url_for('alias'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('alias'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('alias'))

@app.route('/address')
def address():
    all_addresses = session.query(Address).all()
    stmt = select(Category).where(Category.type == "addressType")
    addressType_select = session.execute(stmt).scalars().all()
    owner_select = session.query(Person).all()

    return flask.render_template('address.html', addresses=all_addresses, addressTypes=addressType_select, owners=owner_select)

@app.route('/edit/address/<int:id>', methods=['GET', 'POST'])
def edit_address(id):
    # Retrieve address or return 404
    address = session.get(Address, id)
    if not address:
      return redirect(url_for('address'))

    stmt = select(Category).where(Category.type == "addressType")
    addressType_select = session.execute(stmt).scalars().all()
    owner_select = session.query(Person).all()

    # Serialize to JSON (assuming basic dictionary serialization)
    address_data = {
        'id': address.id,
        'addressType': address.type,
        'name': address.name,
        'type': address.type,
        'address1': address.address1,
        'address2': address.address2,
        'city': address.city,
        'state': address.state,
        'zip5': address.zip5,
        'zip4': address.zip4,
        'owner': address.owner
    }
    return flask.render_template('edit_address.html', address_data=address_data, addressTypes=addressType_select, owners=owner_select)

@app.route('/set_address', methods=['POST'])
def set_address():
  form_data = request.form
  try:
    address = session.execute(select(Address).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if address:
      uporadd = "updated"
      address.type=form_data.get('type')
      address.name=form_data.get('name')
      address.address1=form_data.get('address1')
      address.address2=form_data.get('address2')
      address.city=form_data.get('city')
      address.state=form_data.get('state')
      address.zip5=form_data.get('zip5')
      address.zip4=form_data.get('zip4')
      address.owner=form_data.get('owner')
    else:
      uporadd = "added"
      address = Address(
        type=form_data.get('type'),
        name=form_data.get('name'),
        address1=form_data.get('address1'),
        address2=form_data.get('address2'),
        city=form_data.get('city'),
        state=form_data.get('state'),
        zip5=form_data.get('zip5'),
        zip4=form_data.get('zip4'),
        owner=form_data.get('owner'),
      )
    session.merge(address)
    session.commit()
    flash("Address "+uporadd+" successfully!", "success")
    return redirect(url_for('address'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('address'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('address'))

@app.route('/phone')
def phone():
    all_phones = session.query(Phone).all()
    stmt = select(Category).where(Category.type == "phoneType")
    phoneType_select = session.execute(stmt).scalars().all()
    owner_select = session.query(Person).all()

    return flask.render_template('phone.html', phones=all_phones, phoneTypes=phoneType_select, owners=owner_select)

@app.route('/edit/phone/<int:id>', methods=['GET', 'POST'])
def edit_phone(id):
    phone = session.get(Phone, id)
    if not phone:
      return redirect(url_for('phone'))

    phone_data = {
        'id': phone.id,
        'type': phone.type,
        'phone': phone.phone,
        'owner': phone.owner
    }
    stmt = select(Category).where(Category.type == "phoneType")
    phoneType_select = session.execute(stmt).scalars().all()
    owner_select = session.query(Person).all()
    return flask.render_template('edit_phone.html', phone_data=phone_data, phoneTypes=phoneType_select, owners=owner_select)

@app.route('/set_phone', methods=['POST'])
def set_phone():
  form_data = request.form
  try:
    phone = session.execute(select(Phone).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if phone:
      uporadd = "updated"
      phone.type=form_data.get('type')
      phone.phone=form_data.get('phone')
      phone.owner=form_data.get('owner')
    else:
      uporadd = "added"
      phone = Phone(
        type=form_data.get('type'),
        phone=form_data.get('phone'),
        owner=form_data.get('owner'),
      )
    session.merge(phone)
    session.commit()
    flash("Phone "+uporadd+" successfully!", "success")
    return redirect(url_for('phone'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('phone'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('phone'))

@app.route('/email')
def email():
    all_emails = session.query(Email).all()
    stmt = select(Category).where(Category.type == "emailType")
    emailType_select = session.execute(stmt).scalars().all()
    owner_select = session.query(Person).all()
    return flask.render_template('email.html', emails=all_emails, emailTypes=emailType_select, owners=owner_select)

@app.route('/edit/email/<int:id>', methods=['GET', 'POST'])
def edit_email(id):
    email = session.get(Email, id)
    if not email:
      return redirect(url_for('email'))

    email_data = {
        'id': email.id,
        'type': email.type,
        'email': email.email,
        'owner': email.owner
    }
    stmt = select(Category).where(Category.type == "emailType")
    emailType_select = session.execute(stmt).scalars().all()
    owner_select = session.query(Person).all()
    return flask.render_template('edit_email.html', email_data=email_data, emailTypes=emailType_select, owners=owner_select)

@app.route('/set_email', methods=['POST'])
def set_email():
  form_data = request.form
  try:
    email = session.execute(select(Email).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if email:
      uporadd = "updated"
      email.type=form_data.get('type')
      email.email=form_data.get('email')
      email.owner=form_data.get('owner')
    else:
      uporadd = "added"
      email = Email(
        type=form_data.get('type'),
        email=form_data.get('email'),
        owner=form_data.get('owner'),
      )
    session.merge(email)
    session.commit()
    flash("Email "+uporadd+" successfully!", "success")
    return redirect(url_for('email'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('email'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('email'))

@app.route('/api')
def api():
    all_apis = session.query(Api).all()
    return flask.render_template('api.html', apis=all_apis)

@app.route('/edit/api/<int:id>', methods=['GET', 'POST'])
def edit_api(id):
    api = session.get(Api, id)
    if not api:
      return redirect(url_for('api'))

    api_data = {
        'id': api.id,
        'name': api.name,
        'url': api.url,
        'key': api.key,
        'secret': api.secret,
        'description': api.description
    }
    return flask.render_template('edit_api.html', api_data=api_data)

@app.route('/set_api', methods=['POST'])
def set_api():
  form_data = request.form
  try:
    api = session.execute(select(Api).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if api:
      uporadd = "updated"
      api.name=form_data.get('name')
      api.url=form_data.get('url')
      api.key=form_data.get('key')
      api.secret=form_data.get('secret')
      api.description=form_data.get('description')
    else:
      uporadd = "added"
      api = Api(
        name=form_data.get('name'),
        url=form_data.get('url'),
        key=form_data.get('key'),
        secret=form_data.get('secret'),
        description=form_data.get('description'),
      )
    session.merge(api)
    session.commit()
    flash("Api "+uporadd+" successfully!", "success")
    return redirect(url_for('api'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('api'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('api'))

@app.route('/api_field')
def api_field():
    all_api_fields = session.query(ApiField).all()

    value_options = ValueOptions(session=session)
    options = value_options.get_value_options()

    owner_select = session.query(Api).all()

    return flask.render_template('api_field.html', api_fields=all_api_fields, value_options=options, owners=owner_select)

@app.route('/edit/api_field/<int:id>', methods=['GET', 'POST'])
def edit_api_field(id):
    api_field = session.get(ApiField, id)
    if not api_field:
      return redirect(url_for('api_field'))

    api_field_data = {
        'id': api_field.id,
        'field': api_field.field,
        'value': api_field.value,
        'description': api_field.description,
        'owner': api_field.owner
    }

    value_options = ValueOptions(session=session)
    options = value_options.get_value_options()
    owner_select = session.query(Api).all()
    return flask.render_template('edit_api_field.html', api_field_data=api_field_data, value_options=options, owners=owner_select)

@app.route('/set_api_field', methods=['POST'])
def set_api_field():
  form_data = request.form
  try:
    api_field = session.execute(select(ApiField).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    value_options = ValueOptions(session=session)
    if api_field:
      uporadd = "updated"
      api_field.field=form_data.get('field')
      api_field.value=value_options.get_options_value(form_data.get('value'))
      api_field.description=form_data.get('description')
      api_field.owner=form_data.get('owner')
    else:
      uporadd = "added"
      api_field = ApiField(
        field=form_data.get('field'),
        value=value_options.get_options_value(form_data.get('value')),
        description=form_data.get('description'),
        owner=form_data.get('owner'),
      )
    session.merge(api_field)
    session.commit()
    flash("Api Field "+uporadd+" successfully!", "success")
    return redirect(url_for('api_field'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('api_field'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('api_field'))

@app.route('/view_person')
def view_person():
  people_utils = PeopleUtils(session=session)
  person, aliases, addresses, emails, phones = people_utils.get_all_person()
  return flask.render_template('view_person.html', person=person, aliases=aliases, addresses=addresses, emails=emails, phones=phones)

@app.route('/call_apis')
def call_apis():
  people_utils = PeopleUtils(session=session)
  person = people_utils.get_person()
  person_name = people_utils.get_person_name(person)
  request_api = RequestApi(session=session)
  api = request_api.get_api()
  api_params = request_api.get_api_params()
  return flask.render_template('call_apis.html', api=api, person_name=person_name, api_params=api_params, api_data=None)

@app.route('/call_api', methods=['POST'])
def call_api():
  people_utils = PeopleUtils(session=session)
  person = people_utils.get_person()
  person_name = people_utils.get_person_name(person)
  request_api = RequestApi(session=session)
  api = request_api.get_api()
  api_params = request_api.get_api_params()
  api_data = request_api.get_request()
  return flask.render_template('call_apis.html', api=api, person_name=person_name, api_params=api_params, api_data=api_data)

@app.route('/delete_item', methods=['POST'])
def delete_item():
  form_data = request.form
  id = form_data.get('id')
  table_type = form_data.get('type')
  models = {'person': Person, 'alias': Alias, 'address': Address, 'email': Email, 'phone': Phone, 'category': Category, 'api': Api, 'api_field': ApiField}
  model = models.get(table_type)

  # Specific check for Category child records
  cat_person_count = session.query(Person).filter_by(type=id).count()
  cat_address_count = session.query(Address).filter_by(type=id).count()
  cat_email_count = session.query(Email).filter_by(type=id).count()
  cat_phone_count = session.query(Phone).filter_by(type=id).count()
  if table_type == 'category':
    if cat_person_count > 0:
      flash(f"Cannot delete: {table_type} has {cat_person_count} associated people. Delete them first.", "danger")
      return redirect(url_for('category'))
    if cat_address_count > 0:
      flash(f"Cannot delete: {table_type} has {cat_address_count} associated addresses. Delete them first.", "danger")
      return redirect(url_for('category'))
    if cat_email_count > 0:
      flash(f"Cannot delete: {table_type} has {cat_email_count} associated emails. Delete them first.", "danger")
      return redirect(url_for('category'))
    if cat_phone_count > 0:
      flash(f"Cannot delete: {table_type} has {cat_phone_count} associated phone numbers. Delete them first.", "danger")
      return redirect(url_for('category'))

  # Specific check for Person child records
  alias_count = session.query(Alias).filter_by(owner=id).count()
  address_count = session.query(Address).filter_by(owner=id).count()
  email_count = session.query(Email).filter_by(owner=id).count()
  phone_count = session.query(Phone).filter_by(owner=id).count()
  if table_type == 'person':
    if alias_count > 0:
      flash(f"Cannot delete: {table_type} has {alias_count} associated aliases. Delete them first.", "danger")
      return redirect(url_for('person'))
    if address_count > 0:
      flash(f"Cannot delete: {table_type} has {address_count} associated addresses. Delete them first.", "danger")
      return redirect(url_for('person'))
    if email_count > 0:
      flash(f"Cannot delete: {table_type} has {email_count} associated emails. Delete them first.", "danger")
      return redirect(url_for('person'))
    if phone_count > 0:
      flash(f"Cannot delete: {table_type} has {phone_count} associated phone numbers. Delete them first.", "danger")
      return redirect(url_for('person'))

  # Specific check for Api child records
  api_field_count = session.query(ApiField).filter_by(owner=id).count()
  if table_type == 'api':
    if api_field_count > 0:
      flash(f"Cannot delete: {table_type} has {api_field_count} associated api fields. Delete them first.", "danger")
      return redirect(url_for('api'))

  try:
    item = session.get(model, id)
    session.delete(item)
    session.commit()
    flash(table_type + " deleted successfully!", "success")
    return redirect(url_for(table_type))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for(table_type))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for(table_type))

engine = create_engine(f"sqlite:///{DATABASE}", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def getPerson():
  state = session.get(State, 1)
  current_value = state.person
  default_value = 0
  return current_value or default_value

def getApi():
  state = session.get(State, 1)
  current_value = state.api
  default_value = 0
  return current_value or default_value

@app.route('/set_state', methods=['POST'])
def set_state():
  form_data = request.form
  if form_data is None:
    return redirect(url_for('index'))

  state = session.get(State, 1)
  if state:
    state.person = form_data.get('person')
    state.api = form_data.get('api')
    session.commit()
  return redirect(url_for('index'))

@app.context_processor
def get_state_api():
  all_apis = session.query(Api).all()
  api_dict = {}
  for api in all_apis:
    api_dict[api.id] = api.name
  return dict(state_apis=api_dict)

@app.context_processor
def get_state_persons():
  all_people = session.query(Person).all()
  person_dict = {}
  for person in all_people:
    s1, s2, s3 = person.firstName, person.middleName, person.lastName
    name = " ".join([s for s in [s1, s2, s3] if s])
    person_dict[person.id] = name
  return dict(state_people=person_dict)

@app.context_processor
def inject_site_settings():
  person = getPerson()
  api = getApi()
  return dict(
    selected_person = person,
    selected_api = api,
  )

def initialize_database(engine):
  if not database_exists(engine.url):
    Base.metadata.create_all(bind=engine)

  if session.query(Category).first() is None:
    c1 = Category("contactType", "Missing Person")
    c2 = Category("addressType", "Home")
    c3 = Category("emailType", "Personal")
    c4 = Category("phoneType", "Home")
    session.add(c1)
    session.add(c2)
    session.add(c3)
    session.add(c4)
    session.commit()

  settings = session.get(State, 1)
  if settings is None:
    initial_settings = State(id=1)
    session.add(initial_settings)
    session.commit()

if __name__ == '__main__':
  initialize_database(engine)
  webview.create_window('Missing Persons', app, min_size=(1180, 600), resizable=True, fullscreen=False, text_select=True)
  webview.start(debug=False)

# python -m venv .venv
# .\.venv\Scripts\Activate.ps1
# pip install -r requirements.txt
# python app.py
