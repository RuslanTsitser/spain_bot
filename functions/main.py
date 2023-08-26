# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

import json
from firebase_functions import scheduler_fn, https_fn
import requests
import re


@scheduler_fn.on_schedule(
    schedule="* * * * *",
    timezone=scheduler_fn.Timezone("America/Los_Angeles"),
)
def example(event: scheduler_fn.ScheduledEvent) -> None:
    print(event.job_name)
    print(event.schedule_time)


@https_fn.on_request()
def handle(request: https_fn.Request) -> https_fn.Response:
    php_session_id = get_php_session_id("qf09vee56adsqo35de9rh1ohm1")
    # return response in json format
    return https_fn.Response(
        status=200,
        headers={
            "Content-Type": "application/json",
        },
        content_type="application/json",
        response=json.dumps({
            "php_session_id": php_session_id,
        },)

    )


# URL to request
url = "https://blsspain-russia.com/moscow/english/appointment.php"


def get_php_session_id(php_session_id: str) -> str | None:
    # Cookies
    cookies = {
        "PHPSESSID": php_session_id,
    }
    # Send the GET request with cookies
    response = requests.get(url, cookies=cookies)


# Check if the response contains HTML content
    if "text/html" in response.headers.get("content-type", "").lower():
        # Check if it contains the expected HTML content and not the script
        if "<!DOCTYPE html>" in response.text and \
                "<script>\n\tdocument.location.href='book_appointment.php'\n</script>" not in response.text:
            print("Valid HTML content found in response.")
        else:
            print("HTML content does not match expectations.")
    else:
        print("No HTML content found in response.")
        return None

    # Check if the response contains the expected JavaScript content
    expected_js_content = r'var blocked_dates = \[.*var available_dates = \[\];.*'
    if re.search(expected_js_content, response.text, re.DOTALL):
        print("Expected JavaScript content found in response.")

    # Extract the PHPSESSID value from the response headers
    new_php_session_id = response.cookies.get("PHPSESSID")
    if new_php_session_id:
        print(f"New PHPSESSID value: {new_php_session_id}")

        # Check if available_dates is not empty
        if "var available_dates = [];" not in response.text:
            print("available_dates is not empty.")
        else:
            print("available_dates is empty.")
    else:
        print("JavaScript content does not match expectations.")

    # Extract blocked_dates, available_dates, fullCapicity_dates, and offDates_dates
    js_content = response.text
    blocked_dates = re.findall(
        r'var blocked_dates = (\[.*?\]);', js_content)[0]
    available_dates = re.findall(
        r'var available_dates = (\[.*?\]);', js_content)[0]
    full_capacity_dates = re.findall(
        r'var fullCapicity_dates = (\[.*?\]);', js_content)[0]
    offDates_dates = re.findall(
        r'var offDates_dates = (\[.*?\]);', js_content)[0]

    # Convert the extracted strings to actual Python lists
    blocked_dates = eval(blocked_dates)
    available_dates = eval(available_dates)
    full_capacity_dates = eval(full_capacity_dates)
    offDates_dates = eval(offDates_dates)

    # Print the extracted values
    print("blocked_dates:", blocked_dates)
    print("available_dates:", available_dates)
    print("fullCapicity_dates:", full_capacity_dates)
    print("offDates_dates:", offDates_dates)
    return new_php_session_id
