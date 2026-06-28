import re
from datetime import datetime, date
from datetime import timezone
from dateutil import parser

class DateTimeUtils():

  def format_to_sqlalchemy_date(date_string: str) -> date | None:
    """Parses unpredictable human-written date strings into a Python datetime.date

    object ready for a SQLAlchemy Date column.
    """
    if not date_string or not isinstance(date_string, str):
        return None

    # Step 1: Remove ordinal suffixes (1st, 2nd, 3rd, 4th) so the parser doesn't choke
    cleaned_string = re.sub(
        r"(\d+)(st|nd|rd|th)", r"\1", date_string, flags=re.IGNORECASE
    )

    try:
        # Step 2: Use fuzzy parsing to isolate the date from any surrounding noise
        parsed_datetime = parser.parse(cleaned_string, fuzzy=True)
        return parsed_datetime.date()
    except (ValueError, OverflowError, TypeError):
        return None

  def is_iso_format(date_string):
    try:
        # This will successfully parse "2026-01-31T00:00:00+00:00"
        datetime.fromisoformat(date_string)
        return True
    except (ValueError, TypeError):
        return False
