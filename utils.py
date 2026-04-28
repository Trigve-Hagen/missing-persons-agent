# pip install geopy

from geopy.distance import geodesic

def get_miles(crime_lat, crime_long, suspect_lat, suspect_long):
  # Pre-determined points (Latitude, Longitude)
  CRIME_POINT = (float(crime_lat), float(crime_long))
  SUSPECT_POINT = (float(suspect_lat), float(suspect_long))
  # distance.miles returns the distance in miles
  distance = geodesic(CRIME_POINT, SUSPECT_POINT).miles

  print(f"The distance to the destination is {distance:.2f} miles.")
  return distance

if __name__ == '__main__':
  # Wal1 Walmart in (Store #2059), located at 2200 Greengate Center Cir Greensburg PA
  # Wal2 Walmart in 5929 Georgia Ave Nw, Washington, DC 20011
  wal1_lat = 40.308954
  wal1_long = -79.581448
  wal2_lat = 38.9620920
  wal2_long = -77.0273002
  get_miles(wal1_lat, wal1_long, wal2_lat, wal2_long)
  # outputs
  # Calculates a straight line distance
  # as apposed to a miles by road which would be 210 miles.
  # The distance to the destination is 164.90 miles.

# python -m venv .venv
# .\.venv\Scripts\Activate.ps1
# python utils.py

