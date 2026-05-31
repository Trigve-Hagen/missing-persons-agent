import os
import logging
from classes.model_utils import ModelUtils

class Logging():
  def setup_appdata_logging():
     # 3. Construct the full path to the log file
    log_file_path = ModelUtils.resource_path(os.path.join("logs", "errors.log"))

    # 4. Configure the logging module
    logging.basicConfig(
        # Use as_posix() to prevent Windows backslash escaping errors
        filename=log_file_path.as_posix(),
        level=logging.ERROR,  # Capture only ERROR and CRITICAL logs
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a"  # "a" appends to the file; "w" would overwrite it
    )
