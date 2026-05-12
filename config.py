# config.py

class Config(object):

  #  Database
  #  SQLALCHEMY_DATABASE_URI = "sqlite:///competition.sqlite3"
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  # File Uploads
  UPLOAD_FOLDER = "assets/files/"

  # Allowed file extensions check
  ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
