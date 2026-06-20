from datetime import datetime

def get_dob_from_age(age):
  """create a date from an age to use in the date_of_birth field."""
  current_year = datetime.now().year
  birth_year = current_year - age

  # Format the birthdate as 01/01/YYYY
  # %m = month, %d = day, %Y = 4-digit year
  return f"01/01/{birth_year}"
