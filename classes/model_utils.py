import os
import sys
import re
import unicodedata
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

      logging = os.path.join(base_dir, "logs")
      if not os.path.exists(logging):
        os.makedirs(logging, exist_ok=True)
    else:
      base_dir = os.path.abspath(".")

    return Path(base_dir) / relative_path

  def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

  def machine_name(name):
    # 1. Convert accented characters to ASCII equivalents (e.g., 'é' -> 'e')
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    # 2. Keep only alphanumeric characters, underscores, hyphens, and dots
    # This strips dangerous symbols like /, \, :, *, ?, ", <, >, |
    name = re.sub(r'[^\w\s.-]', '', name).strip()
    # 3. Replace internal spaces or multiple separators with a single underscore
    name = re.sub(r'[-\s]+', '_', name)
    # 4. Remove leading dots to prevent hidden files or directory traversal
    name = name.lstrip('.')
    return name or "default_name"

