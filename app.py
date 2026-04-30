# pip install flask Flask-SQLAlchemy sqlalchemy-utils
import os
import flask
from config import Config
from flask import Flask, request, session, current_app, redirect, flash, render_template, url_for, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, inspect, exc, select, update
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

def object_as_dict(obj):
  return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

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

@app.route('/api/category/<int:id>', methods=['GET'])
def get_category(id):
    # Retrieve category or return 404
    category = session.get(Category, id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    # Serialize to JSON (assuming basic dictionary serialization)
    category_data = {
        'id': category.id,
        'type': category.type,
        'name': category.name
    }
    return jsonify(category_data)

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

  stmt = select(Category).where(Category.type == "contactType")
  contactType_select = session.execute(stmt).scalars().all()

  stmt = select(Category).where(Category.type == "addressType")
  addressType_select = session.execute(stmt).scalars().all()

  stmt = select(Category).where(Category.type == "emailType")
  emailType_select = session.execute(stmt).scalars().all()

  stmt = select(Category).where(Category.type == "phoneType")
  phoneType_select = session.execute(stmt).scalars().all()

  stmt = select(Person).where(Person.contactType == "Missing Person")
  owner_select = session.execute(stmt).scalars().all()

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
  return flask.render_template('person.html', height_options=height_options, weight_options=range(10, 401), hair_color_codes=hair_color_codes, eye_colors=eye_colors, suffixes=name_suffixes, people=all_people, aliases=all_aliases, addresses=all_addresses, emails=all_emails, phones=all_phones, contactTypes=contactType_select, addressTypes=addressType_select, emailTypes=emailType_select, phoneTypes=phoneType_select, owners=owner_select)

@app.route('/api/person/<int:id>', methods=['GET'])
def get_person(id):
    # Retrieve person or return 404
    person = session.get(Person, id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404

    # Serialize to JSON (assuming basic dictionary serialization)
    person_data = {
        'id': person.id,
        'firstName': person.firstName,
        'middleName': person.middleName,
        'lastName': person.lastName,
        'sirName': person.sirName,
        'suffix': person.suffix,
        'contactType': person.contactType,
        'height': person.height,
        'weight': person.weight,
        'hairColor': person.hairColor,
        'eyeColor': person.eyeColor,
        'ssn': person.ssn,
        'gender': person.gender,
        'dob': person.dob,
    }
    return jsonify(person_data)

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
      user.contactType=form_data.get('contactType')
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
        contactType=form_data.get('contactType'),
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
    session.rollback()  # Always rollback on error to reset the session
    error_msg = str(e.orig) # Gets the specific database error message
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('person'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('person'))

@app.route('/api/alias/<int:id>', methods=['GET'])
def get_alias(id):
    # Retrieve alias or return 404
    alias = session.get(Alias, id)
    if not alias:
        return jsonify({'error': 'Alias not found'}), 404

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
    return jsonify(alias_data)

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

@app.route('/api/address/<int:id>', methods=['GET'])
def get_address(id):
    # Retrieve address or return 404
    address = session.get(Address, id)
    if not address:
        return jsonify({'error': 'Address not found'}), 404

    # Serialize to JSON (assuming basic dictionary serialization)
    alias_data = {
        'id': address.id,
        'type': address.type,
        'address1': address.address1,
        'address2': address.address2,
        'city': address.city,
        'state': address.state,
        'zip5': address.zip5,
        'zip4': address.zip4,
        'owner': address.owner
    }
    return jsonify(alias_data)

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

@app.route('/api/email/<int:id>', methods=['GET'])
def get_email(id):
    # Retrieve email or return 404
    email = session.get(Email, id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404

    # Serialize to JSON (assuming basic dictionary serialization)
    email_data = {
        'id': email.id,
        'type': email.type,
        'email': email.email,
        'owner': email.owner
    }
    return jsonify(email_data)

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

@app.route('/api/phone/<int:id>', methods=['GET'])
def get_phone(id):
    # Retrieve phone or return 404
    phone = session.get(Phone, id)
    if not phone:
        return jsonify({'error': 'Phone not found'}), 404

    # Serialize to JSON (assuming basic dictionary serialization)
    phone_data = {
        'id': phone.id,
        'type': phone.type,
        'phone': phone.phone,
        'owner': phone.owner
    }
    return jsonify(phone_data)

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

@app.route('/delete_item', methods=['POST'])
def delete_item():
  form_data = request.form
  id = form_data.get('id')
  table_type = form_data.get('type')
  models = {'person': Person, 'alias': Alias, 'address': Address, 'email': Email, 'phone': Phone, 'category': Category}
  model = models.get(table_type)

  # Specific check for Person child records
  alias_count = session.query(Alias).filter_by(id=id).count()
  address_count = session.query(Address).filter_by(id=id).count()
  email_count = session.query(Email).filter_by(id=id).count()
  phone_count = session.query(Phone).filter_by(id=id).count()
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

  try:
    item = session.get(model, id)
    session.delete(item)
    session.commit()
    flash(table_type + " deleted successfully!", "success")
    if table_type == 'category':
      return redirect(url_for('category'))
    return redirect(url_for('person'))
  except IntegrityError as e:
    session.rollback()  # Always rollback on error to reset the session
    error_msg = str(e.orig) # Gets the specific database error message
    flash(f"Database Error: {error_msg}", "danger")
    if table_type == 'category':
      return redirect(url_for('category'))
    return redirect(url_for('person'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    if table_type == 'category':
      return redirect(url_for('category'))
    return redirect(url_for('person'))


engine = create_engine(f"sqlite:///{DATABASE}", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

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

if __name__ == '__main__':
  initialize_database(engine)
  app.run(debug=True)

# python -m venv .venv
# .\.venv\Scripts\Activate.ps1
# python app.py
