import json
import xmlrpc.client
import ssl
from datetime import datetime, timedelta

url = "http://148.251.132.24:8069"
db = "student"
username = 'student'
password = "student"

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())
common.version()
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context())

# Load event data from JSON file
with open('erasmus/oDaswerk.json') as f:
    events = json.load(f)

# Map of German to English month names
german_to_english_months = {
    'Januar': 'January',
    'Feber': 'February',
    'März': 'March',
    'April': 'April',
    'Mai': 'May',
    'Juni': 'June',
    'Juli': 'July',
    'August': 'August',
    'September': 'September',
    'Oktober': 'October',
    'November': 'November',
    'Dezember': 'December'
}

# Create calendar events from loaded data
for event in events:
    # Parse the start and end dates
    start_date_str, end_date_str = event['Date']

    # Split the start and end date strings
    start_date_parts = start_date_str.split(' - ')
    end_time_parts = end_date_str.split(' ')

    # Parse the start date components
    start_date_components = start_date_parts[0].split(' ')

    start_day = start_date_components[1].rstrip('.')
    start_month = start_date_components[2]

    # Convert German month name to English
    start_month = german_to_english_months.get(start_month, start_month)

    # Reconstruct the start date string
    start_date_str_with_year = f"{start_day} {start_month} {datetime.now().year}"

    # Parse the start date with year and time
    start_date = datetime.strptime(start_date_str_with_year, "%d %B %Y")
    start_time = datetime.strptime(end_time_parts[0], "%H:%M")
    start_datetime = start_date.replace(hour=start_time.hour, minute=start_time.minute)

    # Calculate the end time
    if len(end_time_parts) > 1:  # If end time is provided
        end_time = datetime.strptime(end_time_parts[0], "%H:%M")
        end_datetime = start_date.replace(hour=end_time.hour, minute=end_time.minute)
    else:  # If end time is not provided, add 3 hours to start time
        end_datetime = start_datetime + timedelta(hours=3)

    # Create the event with start and end times
    event_data = {
        'name': event['Title'],
        'start': start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'stop': end_datetime.strftime('%Y-%m-%d %H:%M:%S'),  # Use stop instead of end for XML-RPC
        'description': event['Link'],  # Using the link as the description
        'location': event['Link'],  # Using the link as the location as well
    }
    event_id = models.execute_kw(db, uid, password, 'calendar.event', 'create', [event_data])
    print("New event created with ID:", event_id)