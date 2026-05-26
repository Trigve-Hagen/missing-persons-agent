import os
import sys
from pathlib import Path

class ModelUtils:
  def resource_path(relative_path):
    """
    Resolves a relative path to an absolute path in the Windows AppData
    Roaming folder for compiled apps, or a local 'data' folder for development.
    """

    if getattr(sys, 'frozen', False):
      appdata_path = Path.home() / "AppData" / "Local"
      base_dir = os.path.join(appdata_path, "MissingPersons")
      if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)

      databases = os.path.join(base_dir, "database", "sql_alchemy")
      if not os.path.exists(databases):
        os.makedirs(databases, exist_ok=True)

      uploads = os.path.join(base_dir, "uploads", "files")
      if not os.path.exists(uploads):
        os.makedirs(uploads, exist_ok=True)
    else:
      base_dir = os.path.abspath(".")

    return os.path.join(base_dir, relative_path)

  def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
