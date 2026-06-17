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
import psutil
import os
import sys
import math
import time
import json
import ast
import logging
import subprocess
from werkzeug.utils import secure_filename
from config import Config
from flask import Flask, request, session, current_app, redirect, flash, render_template, url_for, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine, inspect, exc, select, update, func
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database.base import Base
from database.state import State, Task
from database.model import Model, ModelParams, Prompt, Question
from database.apis import Api, ApiField
from database.person import Category, Person, Alias, Email, EmailMessage, Phone, Call, Address, File, Event, Note

from classes.request_api import RequestApi
from classes.selections import Selection
from classes.process_files import ProcessFiles
from classes.people_utils import PeopleUtils, ValueOptions
from classes.resources import Resources
from classes.logging import Logging
from classes.model_utils import ModelUtils
from classes.model_manager import ModelManager
from classes.chat_manager import ChatManager, ChatTester
# from classes.extras.email_manager import EmailManager
from classes.chroma_database import ChromaDatabase
from classes.feed_generator import FeedGenerator
from classes.chroma_manager import PdfRepository, PersonRepository, EventRepository, NoteRepository, Determinator

import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

DATABASE = ModelUtils.resource_path(os.path.join("database", "sql_alchemy", "database.db"))

def resource_path(relative_path):
  """ Get absolute path to resource, works for dev and for PyInstaller """
  try:
      base_path = sys._MEIPASS
  except Exception:
      base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)

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
  resource = Resources()
  create_statements = resource.initialize_determinator(engine=engine)

  data_entities = {}
  for entity, value in create_statements.items():
    if entity in Selection.data_entities:
      data_entities[entity] = value
  determine = Determinator(session=session)
  determine.chunk_create_statements(createStatements=data_entities)

  return flask.render_template('index.html', appData=ModelUtils.resource_path(os.path.join("MissingPersons")))

@app.route('/docs_data')
def docs_data():
  return flask.render_template('docs_data.html')

@app.route('/docs_agents')
def docs_agents():
  return flask.render_template('docs_agents.html')

@app.route('/docs_models')
def docs_models():
  return flask.render_template('docs_models.html')

@app.route('/logs')
def logs():
  logs = []
  LOG_FILE_PATH = ModelUtils.resource_path(os.path.join("logs", "errors.log"))
  if os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, 'r') as file:
      # Read all lines and reverse the list using slice [::-1]
      logs = file.readlines()[::-1]

  page = request.args.get("page", 1, type=int)
  per_page = request.args.get("per_page", 30, type=int)
  offset = (page - 1) * per_page

  total_items = len(logs)
  paginated_logs = logs[offset : offset + per_page]
  total_pages = math.ceil(total_items / per_page)

  return render_template(
    'logs.html',
    logs=paginated_logs,
    page=page,
    total_pages=total_pages,
  )

@app.route('/api/memory', methods=['GET', 'POST'])
def get_memory():
    # Get RAM statistics (in bytes)
    ram = psutil.virtual_memory()

    # Get Hard Drive / Partition statistics for the root directory (in bytes)
    disk = psutil.disk_usage('/')

    # Convert bytes to Gigabytes for readability
    bytes_to_gb = 1024 ** 3

    data = {
        "ram": {
            "total": round(ram.total / bytes_to_gb, 2),
            "available": round(ram.available / bytes_to_gb, 2),
            "used": round(ram.used / bytes_to_gb, 2),
            "percentage_used": ram.percent
        },
        "storage": {
            "total": round(disk.total / bytes_to_gb, 2),
            "used": round(disk.used / bytes_to_gb, 2),
            "free": round(disk.free / bytes_to_gb, 2),
            "percentage_used": disk.percent
        }
    }

    return jsonify({'response': data})

@app.route('/get_rows', methods=['GET', 'POST'])
def get_rows():
  # Parse the JSON data sent in the POST request
  data = request.get_json()

  # Extract the scalar value (e.g., an ID or a name)
  entity_value = data.get('entity')
  match entity_value:
    case "person":
      entities = session.query(Person).all()
      entity_data = [{"id": n.id, "label": PeopleUtils(session=session).get_person_name(n)} for n in entities]
      fields = [c.name for c in Person.__table__.columns if c.name != 'id']
    case "alias":
      entities = session.query(Alias).all()
      entity_data = [{"id": n.id, "label": PeopleUtils(session=session).get_person_name(n)} for n in entities]
      fields = [c.name for c in Alias.__table__.columns if c.name != 'id']
    case "address":
      entities = session.query(Address).all()
      entity_data = [{"id": n.id, "label": n.name} for n in entities]
      fields = [c.name for c in Address.__table__.columns if c.name != 'id']
    case "email":
      entities = session.query(Email).all()
      entity_data = [{"id": n.id, "label": n.email} for n in entities]
      fields = [c.name for c in Email.__table__.columns if c.name != 'id']
    case "phone":
      entities = session.query(Phone).all()
      entity_data = [{"id": n.id, "label": n.phone} for n in entities]
      fields = [c.name for c in Phone.__table__.columns if c.name != 'id']
    case "event":
      entities = session.query(Event).all()
      entity_data = [{"id": n.id, "label": n.name} for n in entities]
      fields = [c.name for c in Event.__table__.columns if c.name != 'id']
    case "note":
      entities = session.query(Note).all()
      entity_data = [{"id": n.id, "label": n.name} for n in entities]
      fields = [c.name for c in Note.__table__.columns if c.name != 'id']

  # jsonify converts the list into a valid JSON response
  return jsonify({
    "fields": fields,
    "entity_data": entity_data
  })

@app.route('/set_entity', methods=['POST'])
def set_entity():
  # Retrieve base identifiers & entity type from the submitted form
  """ entity_type = request.form.get('entity_type')
  entity_id = request.form.get('entity_id')
  field = request.form.get('field')
  value = request.form.get('value') """

  flash(f"This page is not finished. It will have an agent parse the data, list suggestions of key value pairs that you can add to the sqlAlchemy database. This way you can adjust the data before saving it to the vector database. It will filter out None values, decide by the type of column if you can add it functionally and filter out irrelevent data. I'll create a link in the Data Center page so you can look throuh the raw data.", "success")

  flash(f"Create suggestions for Events to save.", 'info')
  flash(f"Create suggestions for Images and Documents into the database.", 'info')
  flash(f"Create suggestions for Notes into the database.", 'info')

  """ if not all([entity_type, entity_id, field]):
    flash('Missing required form parameters.', 'error')
    return redirect(url_for('index'))

  # Map the requested entity type string to the actual SQLAlchemy model
  models = {
    'Person': Person,
    'Address': Address,
    'Phone': Phone,
    'Email': Email,
    'Alias': Alias,
    'event': Event,
    'Note': Note
  }

  model_class = models.get(entity_type)

  if not model_class:
      flash(f'Invalid entity type: {entity_type}', 'error')
      return redirect(url_for('index'))

  # Fetch the specific record from the database
  record = model_class.query.get_or_404(entity_id)

  # Verify that the model actually has the requested column/field
  if not hasattr(record, field):
      flash(f'Field "{field}" does not exist for {entity_type}.', 'error')
      return redirect(url_for('index'))

  # Dynamically update the field and commit to the database
  try:
      setattr(record, field, value)
      session.commit()
      flash(f'{entity_type} updated successfully!', 'success')
  except Exception as e:
      session.rollback()
      flash(f'An error occurred: {str(e)}', 'error') """

  # Redirect to the dashboard or the specific entity view
  return redirect(url_for('data_center'))

@app.route('/file')
def file():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_files = session.query(File).limit(Selection.per_page).offset(offset).all()
  total = session.query(File).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  owner_select = session.query(Person).all()

  return flask.render_template(
    'file.html',
    files=all_files,
    page=page,
    total_pages=total_pages,
    fileTypes=Selection.fileType_select,
    owners=owner_select
  )

@app.route('/edit/file/<int:id>', methods=['GET', 'POST'])
def edit_file(id):
  file = session.get(File, id)
  if not file:
    return redirect(url_for('file'))

  file_data = {
    'id': id,
    'file_id': file.id,
    'type': file.type,
    'filename': file.filename,
    'owner': file.owner
  }

  page = request.args.get("page", 1, type=int)
  per_page = request.args.get("per_page", 10, type=int)
  offset = (page - 1) * per_page

  try:
    pdf_repo = PdfRepository(session=session)
    data, metadatas = pdf_repo.get_chroma_data('file', id)

    total_items = len(data)
    paginated_data = data[offset : offset + Selection.per_page]
    total_pages = math.ceil(total_items / Selection.per_page)
  except Exception as e:
    flash(f"Error connecting to database: {e}", "danger")
    return redirect(url_for('file'))

  owner_select = session.query(Person).all()
  return flask.render_template(
    'edit_file.html',
    edit_id=id,
    file_data=file_data,
    data=paginated_data,
    metadatas=metadatas,
    page=page,
    total_pages=total_pages,
    fileTypes=Selection.fileType_select,
    owners=owner_select
  )

@app.route('/edit/file/vector/<int:id>/<string:file_id>/<string:vector_id>', methods=['GET', 'POST'])
def edit_file_vectors(id, file_id, vector_id):
  try:
    pdf_repo = PdfRepository(session=session)
    data = pdf_repo.get_vector_by_ids([vector_id])
  except Exception as e:
    flash(f"Error connecting to database: {e}", "danger")
    return redirect(url_for('file'))

  vector_data = {
    'id': id,
    'file_id': file_id,
    'vector_id': vector_id,
    'text': data[0]['text'],
    'meta': data[0]['meta'],
    'source': data[0]['source'],
  }
  metadata_dict = data[0]['meta']
  metadata_tuples = list(metadata_dict.items())

  return flask.render_template('edit_file_vector.html', edit_id=id, vector_data=vector_data, meta=metadata_tuples)

""" @app.route('/set_file_vector', methods=['POST'])
def set_file_vector():
  form_data = request.form
  file_id = form_data.get('file_id')

  try:
    vector_id = form_data.get('vector_id')
    pdf_repo = PdfRepository(session=session)
    pdf_repo.update_data_by_id(vector_id)

    flash(f"{vector_id} updated successfully!", "success")
    return redirect(url_for('edit_file_vectors', id=file_id))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('edit_file_vectors', id=file_id))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('edit_file_vectors', id=file_id)) """

@app.route('/set_file_metadata', methods=['POST'])
def set_file_metadata():
  # 1. Grab single IDs
  id = request.form.get('id')
  file_id = request.form.get('file_id')
  vector_id = request.form.get('vector_id')
  content = request.form.get('content')

  # 2. Grab dynamic lists
  keys = request.form.getlist('name[]')
  values = request.form.getlist('value[]')

  # 3. Zip them into a dictionary for easy processing
  metadata = dict(zip(keys, values))

  try:
    pdf_repo = PdfRepository(session=session)
    pdf_repo.update_data_by_id(vector_id=vector_id, content=content, metadata=metadata)
    return redirect(url_for('edit_file_vectors', id=id, file_id=file_id, vector_id=vector_id))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('edit_file_vectors', id=id, file_id=file_id, vector_id=vector_id))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('edit_file_vectors', id=id, file_id=file_id, vector_id=vector_id))

@app.route('/set_file', methods=['POST'])
def set_file():
  form_data = request.form

  if 'file' not in request.files:
    flash(f"No file part", "danger")
    return redirect(url_for('file'))

  file = request.files['file']

  # 2. Check if user actually selected a file
  if file.filename == '':
    flash(f"No selected file", "danger")
    return redirect(url_for('file'))

  # pdf_repo = PdfRepository(session=session)

  # Secure and save the file to sql_alchemy
  if file and ModelUtils.allowed_file(file.filename):
    sec_filename = secure_filename(file.filename)
    filename, filename_ext = os.path.splitext(sec_filename)
    clean_filename = ModelUtils.machine_name(name=filename)
    safe_filename = f"{clean_filename}_{time.time_ns()}{filename_ext}"
    save_path = ModelUtils.resource_path(os.path.join("uploads", "files", safe_filename))
    file.save(save_path)

  try:
    file_record = session.execute(select(File).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if file_record:
      uporadd = "updated"
      file_record.type=form_data.get('type')
      file_record.filename=safe_filename
      file_record.owner=form_data.get('owner')
    else:
      uporadd = "added"
      file_record = File(
        type=form_data.get('type'),
        filename=safe_filename,
        owner=form_data.get('owner'),
      )
    session.merge(file_record)
    session.commit()
    flash(f"File {uporadd} successfully!", "success")
    return redirect(url_for('file'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('file'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('file'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
  user_input = request.json.get('message')
  session_id = request.json.get("session_id", "default_session")

  state = session.get(State, 1)
  model = session.execute(select(Model).filter_by(id = state.model)).scalar_one_or_none()

  try:
    manager = ChatManager(session=session, model=model)
    response = manager.chat_prompt(user_message=user_input, session_id=session_id)
    return jsonify({'response': response})
  except Exception as e:
    return jsonify({'response': "You must have a model selected in Application State and chunks saved to use the chat."})

@app.route('/inspector')
def inspector():
  user_input = ""
  answer = ""

  return flask.render_template(
    'inspector.html',
    user_input=user_input,
    answer=answer,
    database=getDatabase()
  )

@app.route('/task')
def task():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_tasks = session.query(Task).limit(Selection.per_page).offset(offset).all()
  total = session.query(Task).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  return flask.render_template(
    'task.html',
    tasks=all_tasks,
    dateCreated=datetime.now().strftime('%Y-%m-%d'),
    page=page,
    total_pages=total_pages
  )

@app.route('/edit/task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
  # Retrieve task or return 404
  task = session.get(Task, id)
  if not task:
    return redirect(url_for('task'))

  if task.dateCompleted is not None:
      formatted_date = task.dateCompleted.strftime('%Y-%m-%d')
  else:
      formatted_date = None

  task_data = {
    'id': task.id,
    'name': task.name,
    'description': task.description,
    'dateCreated': task.dateCreated.strftime('%Y-%m-%d'),
    'dateCompleted': formatted_date,
  }

  return flask.render_template(
    'edit_task.html',
    edit_id=id,
    task_data=task_data,
  )

@app.route('/set_task', methods=['POST'])
def set_task():
  form_data = request.form

  try:
    task = session.execute(select(Task).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    formatted_dateCreated_date = datetime.strptime(form_data.get('dateCreated'), '%Y-%m-%d')
    if task:
      uporadd = "updated"
      task.name=form_data.get('name')
      task.description=form_data.get('description')
      task.dateCreated=formatted_dateCreated_date
      task.dateCompleted=None
      task.ifComplete=0
    else:
      uporadd = "added"
      task = Task(
        name=form_data.get('name'),
        description=form_data.get('description'),
        dateCreated=formatted_dateCreated_date,
        dateCompleted=None,
        ifComplete=0
      )
    session.merge(task)
    session.commit()

    flash(f"Task {uporadd} successfully!", "success")
    return redirect(url_for('task'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('task'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('task'))

@app.route('/load_code', methods=['POST'])
def run_code_questions():
  process_files = ProcessFiles(session=session)
  process_files.delete_code_chroma()
  process_files.process_and_save_code()
  return redirect(url_for('inspector'))

@app.route('/run_code_optimizer', methods=['POST'])
def run_code_optimizer():
  process_files = ProcessFiles()
  process_files.delete_code_chroma()
  process_files.process_and_save_code()

  if not getPrompt():
    flash(f"Upload a prompt and then set it in State.", "danger")
    return redirect(url_for('task'))

  if not getQuestion():
    flash(f"Upload a question and then set it in State.", "danger")
    return redirect(url_for('task'))

  state = session.get(State, 1)
  model = session.execute(select(Model).filter_by(id = state.model)).scalar_one_or_none()
  prompt = session.execute(select(Prompt).filter_by(id = state.prompt)).scalar_one_or_none()
  question = session.execute(select(Question).filter_by(id = state.question)).scalar_one_or_none()

  manager = ChatManager(session=session, model=model)
  response = manager.suggestions(model=model, prompt=prompt, question=question)
  if response:
    try:
      for item in response.suggestions:
        new_suggestion = Task(
          type="CodeOptimization",
          title=item.title,
          description=item.description,
          ifComplete=0,
        )
        session.add(new_suggestion)
      session.commit()
      flash(f"Successfully saved 10 code suggestions.", "success")
    except json.JSONDecodeError:
      flash(f"Failed to parse LLM response.", "danger")
  else:
    flash(f"No data defined. The database for code optimizations has not been created yet.", "info")

  return redirect(url_for('task'))

@app.route('/run_investigation_optimizer', methods=['POST'])
def run_investigation_optimizer():

  if not os.path.exists(os.path.join(os.path.abspath("."), "database\\investigation_db")):
    flash(f"Upload data to optimize investigation.", "danger")
    return redirect(url_for('task'))

  if not getPrompt():
    flash(f"Upload a prompt and then set it in State.", "danger")
    return redirect(url_for('task'))

  if not getQuestion():
    flash(f"Upload a question and then set it in State.", "danger")
    return redirect(url_for('task'))

  state = session.get(State, 1)
  model = session.execute(select(Model).filter_by(id = state.model)).scalar_one_or_none()
  prompt = session.execute(select(Prompt).filter_by(id = state.prompt)).scalar_one_or_none()
  question = session.execute(select(Question).filter_by(id = state.question)).scalar_one_or_none()

  manager = ChatManager(session=session, model=model)
  response = manager.suggestions(model=model, prompt=prompt, question=question)
  if response:
    try:
      for item in response.suggestions:
        new_suggestion = Task(
          type="InvestigationOptimization",
          title=item.title,
          description=item.description,
          ifComplete=0,
        )
        session.add(new_suggestion)

      session.commit()
      flash(f"Successfully saved 10 investigation suggestions.", "success")
    except json.JSONDecodeError:
      flash(f"Failed to parse LLM response.", "danger")
  else:
    flash(f"No data defined. The database for code optimizations has not been created yet.", "info")

  return redirect(url_for('task'))


@app.route('/set/complete/<int:id>/<int:ifComplete>', methods=['GET', 'POST'])
def set_complete(id, ifComplete):

  try:
    task = session.execute(select(Task).filter_by(id = id)).scalar_one_or_none()
    if task:
      task.ifComplete=ifComplete
      session.merge(task)
      session.commit()

    flash(f"Task updated successfully!", "success")
    return redirect(url_for('task'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('task'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('task'))

@app.route('/model')
def model():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_models = session.query(Model).limit(Selection.per_page).offset(offset).all()
  total = session.query(Model).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  return flask.render_template(
    'model.html',
    models=all_models,
    page=page,
    total_pages=total_pages,
    model_types=Selection.model_types
  )

@app.route('/edit/model/<int:id>', methods=['GET', 'POST'])
def edit_model(id):
  # Retrieve model or return 404
  model = session.get(Model, id)
  if not model:
    return redirect(url_for('model'))

  try:
    # Run the 'ollama show' command
    result = subprocess.run(
        ['ollama', 'show', model.model],
        capture_output=True,
        text=True,
        check=True,
        encoding='utf-8'
    )

    show_data = result.stdout
  except subprocess.CalledProcessError as e:
    show_data = None
    flash(f"Error: {e.stderr.strip()}", "danger")
  except Exception as e:
    show_data = None
    flash(f"Failed to run command: {str(e)}", "danger")

  model_data = {
    'id': model.id,
    'name': model.name,
    'model': model.model,
    'num_ctx': model.num_ctx,
    'temperature': model.temperature,
    'type': model.type
  }

  return flask.render_template(
    'edit_model.html',
    edit_id=id,
    model_data=model_data,
    model_types=Selection.model_types,
    show_data=show_data
  )

@app.route('/set_model', methods=['POST'])
def set_model():
  form_data = request.form
  ollama_model = form_data.get('model')
  manager = ModelManager()
  if not manager.is_model_downloaded(ollama_model):
    manager.download_model(ollama_model)

  try:
    model = session.execute(select(Model).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if model:
      uporadd = "updated"
      model.name=form_data.get('name')
      model.model=ollama_model
      model.num_ctx=form_data.get('num_ctx')
      model.temperature=form_data.get('temperature')
      model.type=form_data.get('type')
    else:
      uporadd = "added"
      model = Model(
        name=form_data.get('name'),
        model=ollama_model,
        num_ctx=form_data.get('num_ctx'),
        temperature=form_data.get('temperature'),
        type=form_data.get('type')
      )
    session.merge(model)
    session.commit()

    flash(f"Model {uporadd} successfully!", "success")
    return redirect(url_for('model'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('model'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('model'))

@app.route('/model_params')
def model_params():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_model_params = session.query(ModelParams).limit(Selection.per_page).offset(offset).all()
  total = session.query(ModelParams).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  owner_select = session.query(Model).all()
  return flask.render_template(
    'model_params.html',
    model_params=all_model_params,
    page=page,
    total_pages=total_pages,
    owners=owner_select
  )

@app.route('/edit/model_params/<int:id>', methods=['GET', 'POST'])
def edit_model_params(id):
  model_params = session.get(ModelParams, id)
  if not model_params:
    return redirect(url_for('model_params'))

  model_params_data = {
    'id': model_params.id,
    'name': model_params.name,
    'value': model_params.value,
    'owner': model_params.owner
  }

  owner_select = session.query(Model).all()
  return flask.render_template('edit_model_params.html', edit_id=id, model_params=model_params_data, owners=owner_select)

@app.route('/set_model_params', methods=['POST'])
def set_model_params():
  form_data = request.form
  try:
    model_params = session.execute(select(ModelParams).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if model_params:
      uporadd = "updated"
      model_params.name=form_data.get('name')
      model_params.value=form_data.get('value')
      model_params.owner=form_data.get('owner')
    else:
      uporadd = "added"
      model_params = ModelParams(
        name=form_data.get('name'),
        value=form_data.get('value'),
        owner=form_data.get('owner'),
      )
    session.merge(model_params)
    session.commit()
    flash(f"Model Parameters {uporadd} successfully!", "success")
    return redirect(url_for('model_params'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('model_params'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('model_params'))

@app.route('/prompt')
def prompt():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_prompts = session.query(Prompt).limit(Selection.per_page).offset(offset).all()
  total = session.query(Prompt).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  return flask.render_template(
    'prompt.html',
    prompts=all_prompts,
    page=page,
    total_pages=total_pages
  )

@app.route('/edit/prompt/<int:id>', methods=['GET', 'POST'])
def edit_prompt(id):
  # Retrieve prompt or return 404
  prompt = session.get(Prompt, id)
  if not prompt:
    return redirect(url_for('prompt'))

  prompt_data = {
      'id': prompt.id,
      'prompt': prompt.prompt,
  }
  return flask.render_template('edit_prompt.html', edit_id=id, prompt_data=prompt_data)

@app.route('/set_prompt', methods=['POST'])
def set_prompt():
  form_data = request.form

  try:
    prompt = session.execute(select(Prompt).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if prompt:
      uporadd = "updated"
      prompt.prompt=form_data.get('prompt')
    else:
      uporadd = "added"
      prompt = Prompt(
        prompt=form_data.get('prompt'),
      )
    session.merge(prompt)
    session.commit()

    flash(f"Prompt {uporadd} successfully!", "success")
    return redirect(url_for('prompt'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('prompt'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('prompt'))

@app.route('/question')
def question():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_questions = session.query(Question).limit(Selection.per_page).offset(offset).all()
  total = session.query(Question).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  return flask.render_template(
    'question.html',
    questions=all_questions,
    page=page,
    total_pages=total_pages
  )

@app.route('/edit/question/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
  # Retrieve question or return 404
  question = session.get(Question, id)
  if not question:
    return redirect(url_for('question'))

  question_data = {
      'id': question.id,
      'question': question.question,
  }
  return flask.render_template('edit_question.html', edit_id=id, question_data=question_data)

@app.route('/set_question', methods=['POST'])
def set_question():
  form_data = request.form

  try:
    question = session.execute(select(Question).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if question:
      uporadd = "updated"
      question.question=form_data.get('question')
    else:
      uporadd = "added"
      question = Question(
        question=form_data.get('question'),
      )
    session.merge(question)
    session.commit()

    flash(f"Question {uporadd} successfully!", "success")
    return redirect(url_for('question'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('question'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('question'))

@app.route('/category')
def category():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_categories = session.query(Category).limit(Selection.per_page).offset(offset).all()
  total = session.query(Category).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  return flask.render_template(
    'category.html',
    categories=all_categories,
    page=page,
    total_pages=total_pages,
    category_types=Selection.category_types
  )

@app.route('/edit/category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
  # Retrieve category or return 404
  category = session.get(Category, id)
  if not category:
    return redirect(url_for('category'))

  category_data = {
      'id': category.id,
      'type': category.type,
      'name': category.name
  }
  return flask.render_template('edit_category.html', edit_id=id, category_data=category_data, category_types=Selection.category_types)

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
    flash(f"Category {uporadd} successfully!", "success")
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
  # Define pagination settings
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page

  stmt = select(Person, Category.name).join(Category, Person.type == Category.id)

  # 2. Get total items and calculate total pages (math.ceil ensures partial pages count as 1)
  total_items = session.scalar(select(func.count()).select_from(stmt.subquery()))
  total_pages = math.ceil(total_items / Selection.per_page)

  # 3. Apply pagination to your statement and execute
  paged_stmt = stmt.limit(Selection.per_page).offset(offset)
  all_people = session.execute(paged_stmt).all()

  people_utils = PeopleUtils(session=session)
  height_options = people_utils.get_height_options()
  contactType_select, hair_colors, eye_colors = people_utils.people_params()
  sir_names, name_suffixes = people_utils.name_params()
  owner_select = session.query(Person).all()

  return flask.render_template(
    'person.html',
    people=all_people,
    page=page,
    total_pages=total_pages,
    contactTypes=contactType_select,
    ethnicities=Selection.abstract_ethnicities,
    primary_languages=Selection.primary_languages,
    height_options=height_options,
    weight_options=range(10, 401),
    hair_colors=hair_colors,
    eye_colors=eye_colors,
    suffixes=name_suffixes,
    sir_names=sir_names,
    owners=owner_select
  )

@app.route('/edit/person/<int:id>', methods=['GET', 'POST'])
def edit_person(id):
  # Retrieve person or return 404
  person = session.get(Person, id)
  if not person:
    return redirect(url_for('person'))

  people_utils = PeopleUtils(session=session)
  height_options = people_utils.get_height_options()
  contactType_select, hair_colors, eye_colors = people_utils.people_params()
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
    'ethnicity': person.ethnicity,
    'primaryLanguage': person.primaryLanguage,
    'ssn': person.ssn,
    'gender': person.gender,
    'dob': person.dob.strftime('%Y-%m-%d'),
    'missing': person.missing.strftime('%Y-%m-%d'),
    'description': person.description,
    'owner': person.owner
  }

  repo = PersonRepository(session=session)
  data, metadatas = repo.get_chroma_data('person', id)

  return flask.render_template(
    'edit_person.html',
    edit_id=id,
    ethnicities=Selection.abstract_ethnicities,
    primary_languages=Selection.primary_languages,
    contactTypes=contactType_select,
    height_options=height_options,
    weight_options=range(10, 401),
    hair_colors=hair_colors,
    eye_colors=eye_colors,
    suffixes=name_suffixes,
    sir_names=sir_names,
    person_data=person_data,
    data=data,
    metadatas=metadatas,
  )

@app.route('/set_person', methods=['POST'])
def set_person():
  form_data = request.form
  try:
    user = session.execute(select(Person).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    formatted_dob_date = datetime.strptime(form_data.get('dob'), '%Y-%m-%d')
    formatted_missing_date = datetime.strptime(form_data.get('missing'), '%Y-%m-%d')
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
      user.ethnicity=form_data.get('ethnicity')
      user.primaryLanguage=form_data.get('primaryLanguage')
      user.ssn=form_data.get('ssn')
      user.gender=form_data.get('gender')
      user.dob=formatted_dob_date
      user.missing=formatted_missing_date
      user.description=form_data.get('description')
      user.owner=form_data.get('owner')
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
        ethnicity=form_data.get('ethnicity'),
        primaryLanguage=form_data.get('primaryLanguage'),
        ssn=form_data.get('ssn'),
        gender=form_data.get('gender'),
        dob=formatted_dob_date,
        missing=formatted_missing_date,
        description=form_data.get('description'),
        owner=form_data.get('owner'),
      )

    session.merge(user)
    session.commit()
    flash(f"Person {uporadd} successfully!", "success")
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

@app.route('/edit/person/vector/<int:id>/<string:file_id>/<string:vector_id>', methods=['GET', 'POST'])
def edit_person_vectors(id, file_id, vector_id):
  try:
    repo = PersonRepository(session=session)
    data = repo.get_vector_by_ids([vector_id])
  except Exception as e:
    flash(f"Error connecting to database: {e}", "danger")
    return redirect(url_for('file'))

  vector_data = {
    'id': id,
    'file_id': file_id,
    'vector_id': vector_id,
    'text': data[0]['text'],
    'meta': data[0]['meta'],
    'source': data[0]['source'],
  }

  metadata_dict = data[0]['meta']
  metadata_tuples = list(metadata_dict.items())

  return flask.render_template('edit_person_vector.html', edit_id=id, vector_data=vector_data, meta=metadata_tuples)

@app.route('/save_to_vector_person', methods=['POST'])
def save_to_vector_person():
  form_data = request.form

  person = session.execute(select(Person).filter_by(id = form_data.get('id'))).scalar_one_or_none()
  repo = PersonRepository(session=session)
  repo.save_person(person)

  return redirect(url_for('edit_person', id=form_data.get('id')))

@app.route('/set_person_metadata', methods=['POST'])
def set_person_metadata():
  # 1. Grab single IDs
  id = request.form.get('id')
  file_id = request.form.get('file_id')
  vector_id = request.form.get('vector_id')
  content = request.form.get('content')

  # 2. Grab dynamic lists
  keys = request.form.getlist('name[]')
  values = request.form.getlist('value[]')

  # 3. Zip them into a dictionary for easy processing
  metadata = dict(zip(keys, values))
  flash(f"Vector Id: {vector_id}", "info")
  flash(f"Metadata: {metadata}", "info")
  flash(f"Content: {content}", "info")

  try:
    repo = PersonRepository(session=session)
    repo.update_data_by_id(vector_id=vector_id, content=content, metadata=metadata)
    return redirect(url_for('edit_person_vectors', id=id, file_id=file_id, vector_id=vector_id))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('edit_person_vectors', id=id, file_id=file_id, vector_id=vector_id))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('edit_person_vectors', id=id, file_id=file_id, vector_id=vector_id))

@app.route('/alias')
def alias():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_aliases = session.query(Alias).limit(Selection.per_page).offset(offset).all()
  total = session.query(Alias).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  owner_select = session.query(Person).all()
  people_utils = PeopleUtils(session=session)
  sir_names, name_suffixes = people_utils.name_params()

  return flask.render_template(
    'alias.html',
    aliases=all_aliases,
    page=page,
    total_pages=total_pages,
    suffixes=name_suffixes,
    sir_names=sir_names,
    owners=owner_select
  )

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

  return flask.render_template('edit_alias.html', edit_id=id, alias_data=alias_data, suffixes=name_suffixes, sir_names=sir_names, owners=owner_select)

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
    flash(f"Alias {uporadd} successfully!", "success")
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
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_addresses = session.query(Address).limit(Selection.per_page).offset(offset).all()
  total = session.query(Address).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  stmt = select(Category).where(Category.type == "addressType")
  addressType_select = session.execute(stmt).scalars().all()
  owner_select = session.query(Person).all()

  return flask.render_template(
    'address.html',
    addresses=all_addresses,
    page=page,
    total_pages=total_pages,
    addressTypes=addressType_select,
    owners=owner_select
  )

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
    'ifCurrent': address.ifCurrent,
    'ifCrimeScene': address.ifCrimeScene,
    'name': address.name,
    'type': address.type,
    'address1': address.address1,
    'address2': address.address2,
    'city': address.city,
    'state': address.state,
    'zip5': address.zip5,
    'zip4': address.zip4,
    'description': address.description,
    'dateFrom': date_from.strftime('%Y-%m-%d') if (date_from := address.dateFrom) else None,
    'dateTo': date_to.strftime('%Y-%m-%d') if (date_to := address.dateTo) else None,
    'owner': address.owner
  }
  return flask.render_template('edit_address.html', edit_id=id, address_data=address_data, addressTypes=addressType_select, owners=owner_select)

@app.route('/set_address', methods=['POST'])
def set_address():
  form_data = request.form
  try:
    address = session.execute(select(Address).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    formatted_dateFrom_date = datetime.strptime(date_from, '%Y-%m-%d') if (date_from := form_data.get('dateFrom')) else None
    formatted_dateTo_date = datetime.strptime(date_to, '%Y-%m-%d') if (date_to := form_data.get('dateTo')) else None
    if_current = 1 if request.form.get("if_current") else 0
    if_crime_scene = 1 if request.form.get("if_crime_scene") else 0
    if address:
      uporadd = "updated"
      address.type=form_data.get('type')
      address.ifCurrent=if_current
      address.ifCrimeScene=if_crime_scene
      address.name=form_data.get('name')
      address.address1=form_data.get('address1')
      address.address2=form_data.get('address2')
      address.city=form_data.get('city')
      address.state=form_data.get('state')
      address.zip5=form_data.get('zip5')
      address.zip4=form_data.get('zip4')
      address.description=form_data.get('description')
      address.dateFrom=formatted_dateFrom_date,
      address.dateTo=formatted_dateTo_date,
      address.owner=form_data.get('owner')
    else:
      uporadd = "added"
      address = Address(
        type=form_data.get('type'),
        ifCurrent=if_current,
        ifCrimeScene=if_crime_scene,
        name=form_data.get('name'),
        address1=form_data.get('address1'),
        address2=form_data.get('address2'),
        city=form_data.get('city'),
        state=form_data.get('state'),
        zip5=form_data.get('zip5'),
        zip4=form_data.get('zip4'),
        description=form_data.get('description'),
        dateFrom=formatted_dateFrom_date,
        dateTo=formatted_dateTo_date,
        owner=form_data.get('owner'),
      )
    session.merge(address)
    session.commit()
    flash(f"Address {uporadd} successfully!", "success")
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
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_phones = session.query(Phone).limit(Selection.per_page).offset(offset).all()
  total = session.query(Phone).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  stmt = select(Category).where(Category.type == "phoneType")
  phoneType_select = session.execute(stmt).scalars().all()
  owner_select = session.query(Person).all()

  return flask.render_template(
    'phone.html',
    phones=all_phones,
    page=page,
    total_pages=total_pages,
    phoneTypes=phoneType_select,
    owners=owner_select
  )

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
  return flask.render_template('edit_phone.html', edit_id=id, phone_data=phone_data, phoneTypes=phoneType_select, owners=owner_select)

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
    flash(f"Phone {uporadd} successfully!", "success")
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
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_emails = session.query(Email).limit(Selection.per_page).offset(offset).all()
  total = session.query(Email).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  stmt = select(Category).where(Category.type == "emailType")
  emailType_select = session.execute(stmt).scalars().all()
  owner_select = session.query(Person).all()

  return flask.render_template(
    'email.html',
    emails=all_emails,
    page=page,
    total_pages=total_pages,
    emailTypes=emailType_select,
    owners=owner_select
  )

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
    return flask.render_template('edit_email.html', edit_id=id, email_data=email_data, emailTypes=emailType_select, owners=owner_select)

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
    flash(f"Email {uporadd} successfully!", "success")
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

@app.route('/event')
def event():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_events = session.query(Event).limit(Selection.per_page).offset(offset).all()
  total = session.query(Event).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  stmt = select(Category).where(Category.type == "eventType")
  eventType_select = session.execute(stmt).scalars().all()
  owner_select = session.query(Person).all()

  return flask.render_template(
    'event.html',
    events=all_events,
    page=page,
    total_pages=total_pages,
    eventTypes=eventType_select,
    owners=owner_select
  )

@app.route('/edit/event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    event = session.get(Event, id)
    if not event:
      return redirect(url_for('event'))

    event_data = {
      'id': event.id,
      'type': event.type,
      'name': event.name,
      'dateFrom': event.dateFrom.strftime('%Y-%m-%d'),
      'dateTo': to.strftime('%Y-%m-%d') if (to := event.dateTo) else None,
      'description': event.description,
      'owner': event.owner
    }

    repo = EventRepository(session=session)
    data, metadatas = repo.get_chroma_data('event', id)

    stmt = select(Category).where(Category.type == "eventType")
    eventType_select = session.execute(stmt).scalars().all()
    owner_select = session.query(Person).all()
    return flask.render_template(
      'edit_event.html',
      edit_id=id,
      event_data=event_data,
      eventTypes=eventType_select,
      owners=owner_select,
      data=data,
      metadatas=metadatas,
    )

@app.route('/set_event', methods=['POST'])
def set_event():
  form_data = request.form
  try:
    event = session.execute(select(Event).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    formatted_dateFrom_date = datetime.strptime(form_data.get('dateFrom'), '%Y-%m-%d')
    formatted_dateTo_date = datetime.strptime(date_str, '%Y-%m-%d') if (date_str := form_data.get('dateTo')) else None
    if event:
      uporadd = "updated"
      event.type=form_data.get('type')
      event.name=form_data.get('name')
      event.dateFrom=formatted_dateFrom_date
      event.dateTo=formatted_dateTo_date
      event.description=form_data.get('description')
      event.owner=form_data.get('owner')
    else:
      uporadd = "added"
      event = Event(
        type=form_data.get('type'),
        name=form_data.get('name'),
        dateFrom=formatted_dateFrom_date,
        dateTo=formatted_dateTo_date,
        description=form_data.get('description'),
        owner=form_data.get('owner'),
      )
    session.merge(event)
    session.commit()
    flash(f"Event {uporadd} successfully!", "success")
    return redirect(url_for('event'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('event'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('event'))

@app.route('/edit/event/vector/<int:id>/<string:file_id>/<string:vector_id>', methods=['GET', 'POST'])
def edit_event_vectors(id, file_id, vector_id):
  try:
    repo = EventRepository(session=session)
    data = repo.get_vector_by_ids([vector_id])
  except Exception as e:
    flash(f"Error connecting to database: {e}", "danger")
    return redirect(url_for('event'))

  vector_data = {
    'id': id,
    'file_id': file_id,
    'vector_id': vector_id,
    'text': data[0]['text'],
    'meta': data[0]['meta'],
    'source': data[0]['source'],
  }

  metadata_dict = data[0]['meta']
  metadata_tuples = list(metadata_dict.items())

  return flask.render_template('edit_event_vector.html', edit_id=id, vector_data=vector_data, meta=metadata_tuples)

@app.route('/save_to_vector_event', methods=['POST'])
def save_to_vector_event():
  form_data = request.form

  event = session.execute(select(Event).filter_by(id = form_data.get('id'))).scalar_one_or_none()
  repo = EventRepository(session=session)
  repo.save_event(event)

  return redirect(url_for('edit_event', id=form_data.get('id')))

@app.route('/set_event_metadata', methods=['POST'])
def set_event_metadata():
  # 1. Grab single IDs
  id = request.form.get('id')
  file_id = request.form.get('file_id')
  vector_id = request.form.get('vector_id')
  content = request.form.get('content')

  # 2. Grab dynamic lists
  keys = request.form.getlist('name[]')
  values = request.form.getlist('value[]')

  # 3. Zip them into a dictionary for easy processing
  metadata = dict(zip(keys, values))
  flash(f"Vector Id: {vector_id}", "info")
  flash(f"Metadata: {metadata}", "info")
  flash(f"Content: {content}", "info")

  try:
    repo = PersonRepository(session=session)
    repo.update_data_by_id(vector_id=vector_id, content=content, metadata=metadata)
    return redirect(url_for('edit_event_vectors', id=id, file_id=file_id, vector_id=vector_id))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('edit_event_vectors', id=id, file_id=file_id, vector_id=vector_id))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('edit_event_vectors', id=id, file_id=file_id, vector_id=vector_id))

@app.route('/note')
def note():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_notes = session.query(Note).limit(Selection.per_page).offset(offset).all()
  total = session.query(Note).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  owner_select = session.query(Person).all()

  return flask.render_template(
    'note.html',
    notes=all_notes,
    page=page,
    total_pages=total_pages,
    owners=owner_select
  )

@app.route('/edit/note/<int:id>', methods=['GET', 'POST'])
def edit_note(id):
  # Retrieve note or return 404
  note = session.get(Note, id)
  if not note:
    return redirect(url_for('note'))

  note_data = {
    'id': note.id,
    'name': note.name,
    'note': note.note,
    'owner': note.owner,
  }

  repo = NoteRepository(session=session)
  data, metadatas = repo.get_chroma_data('note', id)

  owner_select = session.query(Person).all()
  return flask.render_template(
    'edit_note.html',
    edit_id=id,
    note_data=note_data,
    owners=owner_select,
    data=data,
    metadatas=metadatas,
  )

@app.route('/set_note', methods=['POST'])
def set_note():
  form_data = request.form

  try:
    note = session.execute(select(Note).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if note:
      uporadd = "updated"
      note.name=form_data.get('name')
      note.note=form_data.get('note')
      note.owner=form_data.get('owner')
    else:
      uporadd = "added"
      note = Note(
        name=form_data.get('name'),
        note=form_data.get('note'),
        owner=form_data.get('owner'),
      )
    session.merge(note)
    session.commit()

    flash(f"Note {uporadd} successfully!", "success")
    return redirect(url_for('note'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('note'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('note'))

@app.route('/edit/note/vector/<int:id>/<string:file_id>/<string:vector_id>', methods=['GET', 'POST'])
def edit_note_vectors(id, file_id, vector_id):
  try:
    repo = NoteRepository(session=session)
    data = repo.get_vector_by_ids([vector_id])
  except Exception as e:
    flash(f"Error connecting to database: {e}", "danger")
    return redirect(url_for('note'))

  vector_data = {
    'id': id,
    'file_id': file_id,
    'vector_id': vector_id,
    'text': data[0]['text'],
    'meta': data[0]['meta'],
    'source': data[0]['source'],
  }

  metadata_dict = data[0]['meta']
  metadata_tuples = list(metadata_dict.items())

  return flask.render_template('edit_note_vector.html', edit_id=id, vector_data=vector_data, meta=metadata_tuples)

@app.route('/save_to_vector_note', methods=['POST'])
def save_to_vector_note():
  form_data = request.form

  note = session.execute(select(Note).filter_by(id = form_data.get('id'))).scalar_one_or_none()
  repo = NoteRepository(session=session)
  repo.save_note(note)

  return redirect(url_for('edit_note', id=form_data.get('id')))

@app.route('/set_note_metadata', methods=['POST'])
def set_note_metadata():
  # 1. Grab single IDs
  id = request.form.get('id')
  file_id = request.form.get('file_id')
  vector_id = request.form.get('vector_id')
  content = request.form.get('content')

  # 2. Grab dynamic lists
  keys = request.form.getlist('name[]')
  values = request.form.getlist('value[]')

  # 3. Zip them into a dictionary for easy processing
  metadata = dict(zip(keys, values))
  flash(f"Vector Id: {vector_id}", "info")
  flash(f"Metadata: {metadata}", "info")
  flash(f"Content: {content}", "info")

  try:
    repo = PersonRepository(session=session)
    repo.update_data_by_id(vector_id=vector_id, content=content, metadata=metadata)
    return redirect(url_for('edit_note_vectors', id=id, file_id=file_id, vector_id=vector_id))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('edit_note_vectors', id=id, file_id=file_id, vector_id=vector_id))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('edit_note_vectors', id=id, file_id=file_id, vector_id=vector_id))

@app.route('/api')
def api():
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_apis = session.query(Api).limit(Selection.per_page).offset(offset).all()
  total = session.query(Api).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  return flask.render_template(
    'api.html',
    apis=all_apis,
    page=page,
    total_pages=total_pages,
    apiTypes=Selection.api_types
  )

@app.route('/edit/api/<int:id>', methods=['GET', 'POST'])
def edit_api(id):
  api = session.get(Api, id)
  if not api:
    return redirect(url_for('api'))

  api_data = {
    'id': api.id,
    'name': api.name,
    'type': api.type,
    'url': api.url,
    'key': api.key,
    'secret': api.secret,
    'description': api.description
  }
  return flask.render_template(
    'edit_api.html',
    edit_id=id,
    api_data=api_data,
    apiTypes=Selection.api_types
  )

@app.route('/set_api', methods=['POST'])
def set_api():
  form_data = request.form
  try:
    api = session.execute(select(Api).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if api:
      uporadd = "updated"
      api.name=form_data.get('name')
      api.type=form_data.get('type')
      api.url=form_data.get('url')
      api.key=form_data.get('key')
      api.secret=form_data.get('secret')
      api.description=form_data.get('description')
    else:
      uporadd = "added"
      api = Api(
        name=form_data.get('name'),
        type=form_data.get('type'),
        url=form_data.get('url'),
        key=form_data.get('key'),
        secret=form_data.get('secret'),
        description=form_data.get('description'),
      )
    session.merge(api)
    session.commit()
    flash(f"Api {uporadd} successfully!", "success")
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
  page = request.args.get('page', 1, type=int)
  offset = (page - 1) * Selection.per_page
  all_api_fields = session.query(ApiField).limit(Selection.per_page).offset(offset).all()
  total = session.query(ApiField).count()
  total_pages = (total + Selection.per_page - 1) // Selection.per_page

  value_options = ValueOptions(session=session)
  options = value_options.get_value_options()
  owner_select = session.query(Api).all()
  return flask.render_template(
    'api_field.html',
    api_fields=all_api_fields,
    page=page,
    total_pages=total_pages,
    value_options=options,
    owners=owner_select
  )

@app.route('/edit/api_field/<int:id>', methods=['GET', 'POST'])
def edit_api_field(id):
    api_field = session.get(ApiField, id)
    if not api_field:
      return redirect(url_for('api_field'))

    api_field_data = {
      'id': api_field.id,
      'field': api_field.field,
      'value': api_field.value,
      'type': api_field.type,
      'description': api_field.description,
      'owner': api_field.owner
    }

    value_options = ValueOptions(session=session)
    options = value_options.get_value_options()
    owner_select = session.query(Api).all()
    return flask.render_template('edit_api_field.html', edit_id=id, api_field_data=api_field_data, value_options=options, owners=owner_select)

@app.route('/set_api_field', methods=['POST'])
def set_api_field():
  form_data = request.form
  try:
    api_field = session.execute(select(ApiField).filter_by(id = form_data.get('id'))).scalar_one_or_none()
    if api_field:
      uporadd = "updated"
      api_field.field=form_data.get('field')
      api_field.value=form_data.get('value')
      api_field.type=form_data.get('type')
      api_field.description=form_data.get('description')
      api_field.owner=form_data.get('owner')
    else:
      uporadd = "added"
      api_field = ApiField(
        field=form_data.get('field'),
        value=form_data.get('value'),
        type=form_data.get('type'),
        description=form_data.get('description'),
        owner=form_data.get('owner'),
      )
    session.merge(api_field)
    session.commit()
    flash(f"Api Field {uporadd} successfully!", "success")
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

@app.route('/chunk')
def chunk():
  page = request.args.get("page", 1, type=int)
  per_page = request.args.get("per_page", 10, type=int)
  offset = (page - 1) * per_page

  repo = ChromaDatabase(session=session)
  data, metadatas = repo.get_all_chroma_data(getDatabase())

  total_items = len(data)
  paginated_data = data[offset : offset + Selection.per_page]
  total_pages = math.ceil(total_items / Selection.per_page)

  return flask.render_template(
    'chunk.html',
    data=paginated_data,
    metadatas=metadatas,
    page=page,
    total_pages=total_pages,
    available_databases=Selection.available_databases,
    appData=os.path.join(os.environ['LOCALAPPDATA'], "MissingPersons")
  )

@app.route('/dashboard')
def dashboard():
  people_utils = PeopleUtils(session=session)
  person, aliases, addresses, emails, phones = people_utils.get_all_person()
  return flask.render_template('dashboard.html', person=person, aliases=aliases, addresses=addresses, emails=emails, phones=phones)

@app.route('/data_center')
def data_center():
  people_utils = PeopleUtils(session=session)
  person = people_utils.get_person()
  person_name = ""
  api_data = []
  ifParsed = False
  if person:
    person_name = people_utils.get_person_name(person)

  state = session.get(State, 1)
  api = session.execute(select(Api).filter_by(id = state.api)).scalar_one_or_none()
  api_params = session.scalars(select(ApiField).filter_by(owner = api.id)).all()
  if api.type == 'scraper':
    feeds = FeedGenerator(session=session)
    filename, api_data = feeds.get_posts(api, api_params)

    flash(f"Data successfully scraped and saved to {filename}", "info")

  else:
    request_api = RequestApi()
    api_data = request_api.get_request(api, api_params)

    # flash(f"API Data: {api_data}", "info")
    api_data, ifParsed = request_api.filter_data(api_data, state)

    person = session.execute(select(Person).filter_by(id = state.person)).scalar_one_or_none()
    model = session.execute(select(Model).filter_by(id = state.model)).scalar_one_or_none()

    # Start the timer
    start_time = time.perf_counter()

    """ manager = EmailManager(session=session, model=model)
    query = "My internet connection keeps dropping. Can you help?"
    result = manager.run_customer_support(query)
    print(f"Query: {query}")
    print(f"Category: {result['category']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Response: {result['response']}")
    print("\n")
    # Execution Time: 7 minutes 38.77 seconds """

    # flash(f"Response: {response}", "success")

    # End the timer
    end_time = time.perf_counter()
    execution_time = end_time - start_time

    # Split total seconds into whole minutes and remaining seconds
    minutes, seconds = divmod(execution_time, 60)

    flash(f"Execution Time: {int(minutes)} minutes {seconds:.2f} seconds", "success")
    """ if response:
      try:

        for item in response:
          flash(f"Item details: {item}", 'info')
          new_suggestion = Task(
            type="CodeOptimization",
            title=item.title,
            description=item.description,
            ifComplete=0,
          )
          session.add(new_suggestion)
        # session.commit()
        # flash(f"Successfully {response}.", "success")
      except json.JSONDecodeError:
        flash(f"Failed to parse LLM response.", "danger")
    else:
      flash(f"No data defined. The database for code optimizations has not been created yet.", "info") """

  flash("Refactoring to create a continously running agent that uses tooling. The first task would be to search for anyone who is a contact of the missing person and add them as a person of interest. Then search that name and fill in Emails, Phones, Addresses and Aliases. Once the data for one person has been saved. Check their social media and make feeds out of public information. Create events out of any activities listed there. Create a list of people who fit the in the area of the crime scene on the time of the disappearance. Search through other public record keeping systems for information that could mark them as being more apt to be involved in a crime.", "info")

  return flask.render_template(
    'data_center.html',
    api=api,
    person_name=person_name,
    api_params=api_params,
    api_data=api_data,
    root_node=getRootNode(),
    display_type=getDisplayType(),
    if_parsed=ifParsed
  )

@app.route('/filter_data', methods=['POST'])
def filter_data():
  form_data = request.form
  if form_data is None:
    return redirect(url_for('data_center'))

  state = session.get(State, 1)
  api = session.execute(select(Api).filter_by(id = state.api)).scalar_one_or_none()
  api_params = session.scalars(select(ApiField).filter_by(owner = api.id)).all()
  state.display_type = form_data.get('display_type')
  state.root_node = form_data.get('root_node')
  session.commit()

  people_utils = PeopleUtils(session=session)
  person = people_utils.get_person()

  person_name = ""
  if person:
    person_name = people_utils.get_person_name(person)

  request_api = RequestApi()
  api_data = request_api.get_request(api, api_params)
  api_data, ifParsed = request_api.filter_data(api_data, state)

  # flash(f"Variables: {api_data} and {ifParsed}", "danger")

  return flask.render_template('data_center.html', api=api, person_name=person_name, api_params=api_params, api_data=api_data, root_node=form_data.get('root_node'), display_type=form_data.get('display_type'), if_parsed=ifParsed)

@app.route('/create/instance/<int:id>', methods=['GET', 'POST'])
def create_instance(id):
  model = session.get(Model, id)
  model_params = session.execute(select(ModelParams).filter_by(id = id)).all()

  parameters = {k: v for k, v in model_params}
  manager = ModelManager()
  manager.create_model(model, parameters)

  all_models = session.query(Model).all()

  model_types = [
    ('ollama', 'Ollama'),
  ]
  return flask.render_template('model.html', models=all_models, model_types=model_types)

@app.route('/set/state/<string:type>/<int:id>', methods=['GET', 'POST'])
def link_set_state(type, id):

  state = session.get(State, 1)
  if state:
    try:
      if type == 'model':
        state.model = id
      elif type == 'person':
        state.person = id
      elif type == 'prompt':
        state.prompt = id
      elif type == 'question':
        state.question = id
      else:
        state.api = id

      session.commit()
      flash(f"State set successfully!", "success")
      return redirect(url_for(type))
    except IntegrityError as e:
      session.rollback()
      error_msg = str(e.orig)
      flash(f"Database Error: {error_msg}", "danger")
      return redirect(url_for(type))
    except Exception as e:
      session.rollback()
      flash(f"An unexpected error occurred: {str(e)}", "danger")
      return redirect(url_for(type))

@app.route('/delete_vector_item', methods=['POST'])
def delete_vector_item():
  form_data = request.form
  entity_id = form_data.get('entity_id')
  vector_id = form_data.get('vector_id')
  edit_path = form_data.get('edit_path')

  try:
    manager = ChromaDatabase(session=session)
    manager.delete_vector_by_id(ids=[vector_id])
    flash(vector_id + " deleted successfully!", "success")
    return redirect(url_for(edit_path, id=entity_id))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for(edit_path, id=entity_id))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for(edit_path, id=entity_id))

@app.route('/delete_file_vector_item', methods=['POST'])
def delete_file_vector_item():
  form_data = request.form
  file_id = form_data.get('file_id')
  source = form_data.get('source')

  try:
    manager = PdfRepository(session=session)
    manager.delete_file_by_source(source)
    flash(source + " deleted successfully!", "success")
    return redirect(url_for('edit_file', id=file_id))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('edit_file', id=file_id))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('edit_file', id=file_id))

@app.route('/save_to_vector_file', methods=['POST'])
def save_to_vector_file():
  form_data = request.form
  file_id=form_data.get('file_id')
  filename=form_data.get('filename')

  try:
    pdf_repo = PdfRepository(session=session)
    file_record = session.execute(select(File).filter_by(id = file_id)).scalar_one_or_none()
    # save the file to vector_store
    pdf_repo.save_document(record=file_record, filename=filename)
    flash(filename + " saved to vector db successfully!", "success")
    return redirect(url_for('edit_file', id=file_id))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('edit_file', id=file_id))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('edit_file', id=file_id))

@app.route('/delete_item', methods=['POST'])
def delete_item():
  form_data = request.form
  id = form_data.get('id')
  table_type = form_data.get('type')

  available_models = {
    'person': Person, 'alias': Alias, 'address': Address, 'email': Email,
    'phone': Phone, 'file': File, 'category': Category, 'api': Api,
    'task': Task, 'event': Event, 'note': Note,
    'api_field': ApiField, 'model': Model, 'model_params': ModelParams,
    'prompt': Prompt, 'question': Question
  }

  model = available_models.get(table_type)

  # Specific check for Category child records
  cat_person_count = session.query(Person).filter_by(type=id).count()
  cat_address_count = session.query(Address).filter_by(type=id).count()
  cat_email_count = session.query(Email).filter_by(type=id).count()
  cat_phone_count = session.query(Phone).filter_by(type=id).count()
  cat_file_count = session.query(File).filter_by(type=id).count()
  cat_event_count = session.query(Event).filter_by(type=id).count()
  if table_type == 'category':
    if int(id) <= 6:
      flash(f"You cannot delete initial categories. You can only update the name.", "danger")
      return redirect(url_for('category'))
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
    if cat_file_count > 0:
      flash(f"Cannot delete: {table_type} has {cat_file_count} associated files. Delete them first.", "danger")
      return redirect(url_for('category'))
    if cat_event_count > 0:
      flash(f"Cannot delete: {table_type} has {cat_event_count} associated events. Delete them first.", "danger")
      return redirect(url_for('category'))

  # Specific check for Person child records
  alias_count = session.query(Alias).filter_by(owner=id).count()
  address_count = session.query(Address).filter_by(owner=id).count()
  email_count = session.query(Email).filter_by(owner=id).count()
  phone_count = session.query(Phone).filter_by(owner=id).count()
  file_count = session.query(File).filter_by(owner=id).count()
  event_count = session.query(Event).filter_by(owner=id).count()
  note_count = session.query(Note).filter_by(owner=id).count()
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
    if file_count > 0:
      flash(f"Cannot delete: {table_type} has {file_count} associated files. Delete them first.", "danger")
      return redirect(url_for('person'))
    if event_count > 0:
      flash(f"Cannot delete: {table_type} has {event_count} associated events. Delete them first.", "danger")
      return redirect(url_for('person'))
    if note_count > 0:
      flash(f"Cannot delete: {table_type} has {note_count} associated notes. Delete them first.", "danger")
      return redirect(url_for('person'))

  # Specific check for Api child records
  api_field_count = session.query(ApiField).filter_by(owner=id).count()
  if table_type == 'api':
    if api_field_count > 0:
      flash(f"Cannot delete: {table_type} has {api_field_count} associated api fields. Delete them first.", "danger")
      return redirect(url_for('api'))

  # Specific check for Model child records
  model_params_count = session.query(ModelParams).filter_by(owner=id).count()
  if table_type == 'model':
    if model_params_count > 0:
      flash(f"Cannot delete: {table_type} has {model_params_count} associated api fields. Delete them first.", "danger")
      return redirect(url_for('model'))

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

@app.route('/resources')
def resources():
  resource = Resources()
  models = resource.ollama_models()

  state = session.get(State, 1)
  resources = [
    ("Files Size", state.files_size),
    ("Sql Alchemy Database", state.sql_alchemy_database_size),
    ("Chroma Database", state.chroma_database_size),
    ("Ollama Models", state.ollama_models_size),
  ]

  return flask.render_template('resources.html', resources=resources, models=models)

@app.route('/set_resources', methods=['POST'])
def set_resources():
  state = session.get(State, 1)
  resource = Resources()
  if state:
    state.files_size = resource.files_size()
    state.sql_alchemy_database_size = resource.sql_alchemy_database()
    state.chroma_database_size = resource.chroma_database()
    state.ollama_models_size = resource.ollama_models_size()
    session.commit()

  return redirect(url_for('resources'))

@app.route('/delete_model', methods=['POST'])
def delete_model():
  form_data = request.form
  item = form_data.get('item')

  # Specific check for Api child records
  model_count = session.query(Model).filter_by(type=item).count()
  if model_count > 0:
    flash(f"Cannot delete: {item} has {model_count} associated models. Delete them first.", "danger")
    return redirect(url_for('resources'))

  try:
    manager = ModelManager()
    manager.remove_model(item)
    flash(item + " deleted successfully!", "success")
    return redirect(url_for('resources'))
  except IntegrityError as e:
    session.rollback()
    error_msg = str(e.orig)
    flash(f"Database Error: {error_msg}", "danger")
    return redirect(url_for('resources'))
  except Exception as e:
    session.rollback()
    flash(f"An unexpected error occurred: {str(e)}", "danger")
    return redirect(url_for('resources'))

engine = create_engine(f"sqlite:///{DATABASE}", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

def getPrompt():
  state = session.get(State, 1)
  prompt = session.execute(select(Prompt).filter_by(id = state.prompt)).scalar_one_or_none()
  return prompt

def getQuestion():
  state = session.get(State, 1)
  prompt = session.execute(select(Question).filter_by(id = state.question)).scalar_one_or_none()
  return prompt

def getDatabase():
  state = session.get(State, 1)
  current_value = state.database
  default_value = "investigation_db"
  return current_value or default_value

def getLoader():
  state = session.get(State, 1)
  current_value = state.loader
  default_value = "docling"
  return current_value or default_value

def getChunkSize():
  state = session.get(State, 1)
  current_value = state.chunk_size
  default_value = 2000
  return current_value or default_value

def getChunkOverlap():
  state = session.get(State, 1)
  current_value = state.chunk_overlap
  default_value = 100
  return current_value or default_value

def getProcessor():
  state = session.get(State, 1)
  current_value = state.processor
  default_value = "cpu"
  return current_value or default_value

def getRootNode():
  state = session.get(State, 1)
  current_value = state.root_node
  default_value = ""
  return current_value or default_value

def getDisplayType():
  state = session.get(State, 1)
  current_value = state.display_type
  default_value = "json"
  return current_value or default_value

def getTheme():
  state = session.get(State, 1)
  current_value = state.theme
  default_value = "light"
  return current_value or default_value

@app.route('/application_state')
def application_state():
  all_apis = session.query(Api).all()
  all_people = session.query(Person).all()
  all_models = session.query(Model).all()
  all_prompts = session.query(Prompt).all()
  all_questions = session.query(Question).all()
  all_themes={
    "light": "Light",
    "dark": "Dark"
  }
  state = session.get(State, 1)

  return flask.render_template(
    'application_state.html',
    state=state,
    available_devices=Selection.available_devices,
    available_databases=Selection.available_databases,
    available_collections=Selection.available_collections,
    available_themes=all_themes,
    people=all_people,
    apis=all_apis,
    models=all_models,
    prompts=all_prompts,
    questions=all_questions,
    appData=os.path.join(os.environ['LOCALAPPDATA'], "MissingPersons")
  )

@app.route('/set_vector_db', methods=['POST'])
def set_vector_db():
  form_data = request.form
  if form_data is None:
    return redirect(url_for('chunk'))

  state = session.get(State, 1)
  if state:
    state.database = form_data.get('database')
    session.commit()

  return redirect(url_for('chunk'))

@app.route('/set_application_state', methods=['POST'])
def set_application_state():
  form_data = request.form
  if form_data is None:
    return redirect(url_for('application_state'))

  state = session.get(State, 1)
  if state:
    state.processor = form_data.get('processor')
    state.theme = form_data.get('theme')
    state.person = form_data.get('person')
    state.api = form_data.get('api')
    state.model = form_data.get('model')
    state.prompt = form_data.get('prompt')
    state.question = form_data.get('question')
    state.database = form_data.get('database')
    state.collection = form_data.get('collection')
    session.commit()

  return redirect(url_for('application_state'))

@app.route('/set_state', methods=['POST'])
def set_state():
  form_data = request.form
  if form_data is None:
    return redirect(url_for('index'))

  path = form_data.get('path')
  state = session.get(State, 1)
  if state:
    state.processor = form_data.get('processor')
    session.commit()

  if 'edit_id' in request.form:
    return redirect(url_for(path, id=form_data.get('edit_id')))
  else:
    return redirect(url_for(path))

@app.context_processor
def get_state_processor():
  return dict(state_processors=Selection.available_devices)

@app.context_processor
def inject_site_settings():
  processor = getProcessor()
  database = getDatabase()
  theme = getTheme()
  return dict(
    state_path = request.endpoint,
    selected_processor = processor,
    selected_database = database,
    selected_theme = theme,
  )

def initialize_database(engine):
  if not database_exists(engine.url):
    Base.metadata.create_all(bind=engine)

  if session.query(Category).first() is None:
    c1 = Category("contactType", "Missing Person") # 1
    c2 = Category("contactType", "Person of Interest") # 2
    c3 = Category("addressType", "Task Type") # 3
    c4 = Category("emailType", "Task Type") # 4
    c5 = Category("phoneType", "Task Type") # 5
    c6 = Category("eventType", "Task Type") # 6
    session.add(c1)
    session.add(c2)
    session.add(c3)
    session.add(c4)
    session.add(c5)
    session.add(c6)
    session.commit()

  settings = session.get(State, 1)
  if settings is None:
    initial_settings = State(id=1)
    session.add(initial_settings)
    session.commit()

  if session.query(Person).first() is None:
    p1 = Person(
      type=1, sirName="", firstName="Nancy", middleName="", lastName="Guthrie",
      suffix="", height="64", weight="150", hairColor="Brown", eyeColor="Blue", ssn="",
      description="", gender="female", dob=datetime(1942, 1, 27),
      missing=datetime(2026, 2, 1), owner=0, ethnicity="white",
      primaryLanguage="english"
    )
    session.add(p1)

    state = session.get(State, 1)
    state.person = 1
    session.commit()

  if session.query(Api).first() is None:
    a1 = Api(
      name="FBI", type="api", url="https://api.fbi.gov/wanted/v1/list",
      key='', secret='', description=''
    )
    session.add(a1)

    state = session.get(State, 1)
    state.api = 1
    state.root_node = "items"
    state.display_type = "table"
    session.commit()

  if session.query(ApiField).first() is None:
    a1 = ApiField(
      field="title", value="Nancy Guthrie", type='', description='', owner=1
    )
    session.add(a1)
    session.commit()

  """ if session.query(Model).first() is None:
    resource = Resources()
    models = resource.ollama_models()
    for model in models['models']:
      m1 = Model(name=model.model, model=model.model, type="ollama", system="")
      session.add(m1)
      session.commit() """

  if session.query(Prompt).first() is None:
    p1 = Prompt(
      prompt="You are an expert criminal investigator, forensic analyst, and search-and-rescue strategist. Your objective is to help me optimize my approach to an active missing person case. Analyze the scenario detailed in the question below and provide 10 highly actionable, evidence-based suggestions that prioritize investigative efficiency and subject safety."
    )
    session.add(p1)
    state = session.get(State, 1)
    state.prompt = 1
    session.commit()

  if session.query(Question).first() is None:
    q1 = Question(
      question="I am investigating the disappearance of Nancy Guthrie. What are 10 specific investigative steps, technological strategies, or procedural optimizations I can use to maximize our chances of locating her safely?"
    )
    session.add(q1)
    state = session.get(State, 1)
    state.question = 1
    session.commit()

def update_height(window):
    """Fetches height and passes it to the active HTML page."""
    height = window.height
    # Executes JS function defined in your HTML
    window.evaluate_js(f"if (typeof updateHtmlHeight === 'function') {{ updateHtmlHeight({height}); }}")

def on_loaded(window):
    """Triggered when the page finishes loading."""
    update_height(window)

def on_resized(width, height):
    """Triggered whenever the user resizes the window."""
    # active_window gets the current window object
    window = webview.active_window()
    if window:
        update_height(window)

if getattr(sys, 'frozen', False):
  import pyi_splash

  if pyi_splash.is_alive():
    pyi_splash.close()

if __name__ == '__main__':
  initialize_database(engine)

  Logging.setup_appdata_logging()
  window = webview.create_window('Missing Persons', app, min_size=(1180, 650), resizable=True, fullscreen=False, text_select=True)
  # Bind the events to the Python functions
  window.events.resized += on_resized
  window.events.loaded += on_loaded

  webview.start(debug=True)

# python -m venv .venv
# .\.venv\Scripts\Activate.ps1
# pip install -r requirements.txt
# python app.py
