import os
import platform
import ollama
from flask import flash

class OllamaManager:
  def __init__(self):
    self.client = ollama.Client()

  def initialize():
    pass

  def get_models(self):
    """Lists all locally downloaded models."""
    models = []
    try:
      models = self.client.list()
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

  def create_model(self, name, config):
    print(f"Creating model: {name}...")
    ollama.create(
        model=name,
        from_=config["from"],
        system=config["system"],
        parameters=config["parameters"]
    )
    print(f"Successfully built {name}")

  def stop_model(self, model_name: str):
    """Stops/Unloads a model from memory."""
    print(f"Stopping {model_name}...")
    # Setting keep_alive=0 purges the model from memory
    self.client.generate(model_name, keep_alive=0)
    print(f"Model {model_name} stopped.")

  def remove_model(self, model_name: str):
    """Removes a model from the system."""
    try:
      self.client.delete(model_name)
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

# --- Usage Example ---
# manager = OllamaManager()

# Example workflow
# manager.download_model("llama3")
# manager.list_models()
# manager.stop_model("llama3")
# manager.remove_model("llama3")
# manager.get_ollama_storage_gb()
