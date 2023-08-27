# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from datetime import datetime
import json
from firebase_functions import scheduler_fn, https_fn
import requests
import re

from functions.app_firestore import get_latest_firestore_data, save_latest_firestore_data
from functions.app_telegram_bot import send_message_telegram
from functions.classes import FirestoreData, MainData


@scheduler_fn.on_schedule(
    # every minute
    schedule="*/1 * * * *",
    timezone=scheduler_fn.Timezone("America/Los_Angeles"),
)
def example(event: scheduler_fn.ScheduledEvent) -> None:
    main_data = get_main_data(None)
    if main_data is None:
        return
    save_latest_firestore_data(main_data.firestore_data)
    if (main_data.available_dates != []):
        send_message_telegram('php_session_id: ' +
                              main_data.new_php_session_id + '\n' + 'available_dates: ' + str(main_data.available_dates) + '\n' + 'full_capacity_dates: ' + str(main_data.full_capacity_dates) + '\n' + 'offDates_dates: ' + str(main_data.offDates_dates) + '\n' + 'old_php_session_id: ' + main_data.old_php_session_id)
    elif (main_data.firestore_data.is_expired & (main_data.firestore_data.is_sent == False)):
        firestore_data = FirestoreData(
            php_session_id=main_data.new_php_session_id,
            current_date=datetime.now(),
            is_expired=True,
            is_sent=True
        )
        save_latest_firestore_data(firestore_data)
        send_message_telegram('Token expired' + '\n' +
                              'php_session_id: ' + main_data.new_php_session_id)


@https_fn.on_request()
def handle(request: https_fn.Request) -> https_fn.Response:
    request_php_token = request.args.get("php_token")
    main_data = get_main_data(request_php_token)
    if main_data is None:
        return https_fn.Response(
            status=200,
            headers={
                "Content-Type": "application/json",
            },
            content_type="application/json",
            response=json.dumps({
                "error": "No firestore data",
            },)
        )

    # save latest firestore data
    save_latest_firestore_data(main_data.firestore_data)
    if (main_data.firestore_data.is_expired):
        send_message_telegram('Token expired' + '\n' +
                              'php_session_id: ' + main_data.new_php_session_id)
    else:
        send_message_telegram('php_session_id: ' +
                              main_data.new_php_session_id + '\n' + 'available_dates: ' + str(main_data.available_dates) + '\n' + 'full_capacity_dates: ' + str(main_data.full_capacity_dates) + '\n' + 'offDates_dates: ' + str(main_data.offDates_dates) + '\n' + 'old_php_session_id: ' + main_data.old_php_session_id)

    # return response in json format
    return https_fn.Response(
        status=200,
        headers={
            "Content-Type": "application/json",
        },
        content_type="application/json",
        response=json.dumps({
            "php_session_id": main_data.old_php_session_id,
            "new_php_session_id": main_data.new_php_session_id,
            "is_expired": main_data.firestore_data.is_expired,
            "available_dates": main_data.available_dates,
            "full_capacity_dates": main_data.full_capacity_dates,
            "offDates_dates": main_data.offDates_dates,
            "blocked_dates": main_data.blocked_dates,
        },)

    )


# URL to request
url = "https://blsspain-russia.com/moscow/english/appointment.php"


def get_php_session_id(php_session_id: str) -> MainData:
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
            firestore_data = FirestoreData(
                php_session_id=php_session_id,
                current_date=datetime.now(),
                is_expired=True
            )
            return MainData(old_php_session_id=php_session_id,
                            new_php_session_id=php_session_id,
                            blocked_dates=[],
                            available_dates=[],
                            full_capacity_dates=[],
                            offDates_dates=[],
                            firestore_data=firestore_data
                            )
    else:
        print("No HTML content found in response.")
        firestore_data = FirestoreData(
            php_session_id=php_session_id,
            current_date=datetime.now(),
            is_expired=True
        )
        return MainData(old_php_session_id=php_session_id,
                        new_php_session_id=php_session_id,
                        blocked_dates=[],
                        available_dates=[],
                        full_capacity_dates=[],
                        offDates_dates=[],
                        firestore_data=firestore_data
                        )

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
    current_date = datetime.now()
    firestore_data = FirestoreData(
        php_session_id=new_php_session_id,
        current_date=current_date
    )

    # Print the extracted values
    result = MainData(old_php_session_id=php_session_id,
                      new_php_session_id=new_php_session_id,
                      blocked_dates=blocked_dates,
                      available_dates=available_dates,
                      full_capacity_dates=full_capacity_dates,
                      offDates_dates=offDates_dates,
                      firestore_data=firestore_data
                      )
    return result


def get_main_data(request_php_token: str | None) -> MainData | None:
    print(request_php_token)
    if (request_php_token is None):
        firestore_data = get_latest_firestore_data()
        print(firestore_data)
        if firestore_data is None:
            return None
        return get_php_session_id(firestore_data.php_session_id)
    else:
        return get_php_session_id(request_php_token)
