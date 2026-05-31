import os
import re
import platform
import ollama
import json
import sys
from flask import flash
from sqlalchemy import select
from database.state import State
from database.model import Model, Prompt, Question
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from classes.model_utils import ModelUtils
from classes.chroma_database import ChromaDatabase
from datetime import datetime
from langchain_community.llms import Ollama
from langchain_core.output_parsers import JsonOutputParser

class ModelManager:
  def get_models(self):
    """Lists all locally downloaded models."""
    models = []
    try:
      client = ollama.Client()
      models = client.list()
    except Exception as e:
      flash(f"Error fetching models: {e}", "danger")

    return models

  def is_model_downloaded(self, name):
    # checks if the model is downloaded already.
    local_models = ollama.list()
    for model in local_models['models']:
      if model['model'] == name:
        return True
    return False

  def download_model(self, model_name: str):
    # Downloads/Pulls an Ollama model.
    try:
      ollama.pull(model_name)
      flash(f"Model {model_name} downloaded successfully.", "success")
      return True
    except ollama.ResponseError as e:
      if "404" in str(e):
        flash(f"Model '{model_name}' does not exist on ollama.com.", "danger")
      else:
        flash(f"An error occurred: {e}", "danger")
      return False
    except Exception as e:
      flash(f"Error fetching models: {e}", "danger")
      return False

  def create_model(self, model: Model, parameters):
    try:
      ollama.create(
          model=ModelUtils.machine_name(name=model.name),
          from_=model.model,
          system=model.system,
          parameters=parameters
      )
      flash(f"Model {model.name} created successfully.", "success")
      return True
    except Exception as e:
      flash(f"Error creating model: {e}", "danger")
      return False

  def remove_model(self, model_name: str):
    """Removes a model from the system."""
    try:
      client = ollama.Client()
      client.delete(model_name)
      flash(f"Model {model_name} removed.", "success")
      return True
    except Exception as e:
      flash(f"Error removing model: {e}", "danger")
      return False

  def get_ollama_storage_gb(self):
    """ Returns the total size of Ollama's model storage in Gigabytes. """
    # Determine default path based on OS
    home = os.path.expanduser("~")
    system = platform.system()

    if system == "Windows":
      path = os.path.join(home, ".ollama", "models")
    elif system == "Darwin":  # macOS
      path = os.path.join(home, ".ollama", "models")
    else:  # Linux (standard default)
      path = "/usr/share/ollama/.ollama/models"
      if not os.path.exists(path):
        path = os.path.join(home, ".ollama", "models")

    # If the user has set a custom path via OLLAMA_MODELS, use that instead
    path = os.environ.get("OLLAMA_MODELS", path)

    if not os.path.exists(path):
      return 0.0

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
      for f in filenames:
        fp = os.path.join(dirpath, f)
        # skip if it is a symbolic link
        if not os.path.islink(fp):
          total_size += os.path.getsize(fp)

    # Convert bytes to Gigabytes
    return total_size / (1024**3)
