# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from datetime import datetime
import json
from firebase_functions import scheduler_fn, https_fn
import requests
import re

from app_firestore import get_latest_firestore_data, save_latest_firestore_data
from app_telegram_bot import send_message_telegram
from classes import FirestoreData, MainData
from const.key import APPOINTMENT_URL
from app_firestore import get_list_of_documents_ids
from app_firestore import set_is_sent


@scheduler_fn.on_schedule(
    # every minute
    schedule="*/1 * * * *",
    timezone=scheduler_fn.Timezone("America/Los_Angeles"),
)
def example(event: scheduler_fn.ScheduledEvent) -> None:
    document_ids = get_list_of_documents_ids()
    for document_id in document_ids:
        firestore_data = get_latest_firestore_data(document_id)
        if firestore_data is None:
            continue
        main_data = get_main_data(
            firestore_data.php_session_id, document_id)
        if main_data is None:
            continue
        save_latest_firestore_data(main_data.firestore_data, document_id)
        if (main_data.firestore_data.is_expired and main_data.firestore_data.is_sent == False):
            set_is_sent(document_id, True)

            send_message_telegram(
                telegram_id=document_id,
                message='Token expired' + '\n' +
                'php_session_id: ' + main_data.new_php_session_id)
        elif (main_data.available_dates != []):

            send_message_telegram(
                telegram_id=document_id,
                message='php_session_id: ' +
                main_data.new_php_session_id + '\n' + 'available_dates: ' + str(main_data.available_dates) + '\n' + 'full_capacity_dates: ' + str(main_data.full_capacity_dates) + '\n' + 'offDates_dates: ' + str(main_data.offDates_dates) + '\n' + 'old_php_session_id: ' + main_data.old_php_session_id)


@https_fn.on_request()
def handle(request: https_fn.Request) -> https_fn.Response:
    request_php_token = request.args.get("php_token")
    telegram_id = request.args.get("telegram_id")
    if (telegram_id is None):
        return https_fn.Response(
            status=400,
            headers={
                "Content-Type": "application/json",
            },
            content_type="application/json",
            response=json.dumps({
                "error": "No telegram_id",
            },)
        )
    main_data = get_main_data(request_php_token, telegram_id)
    if main_data is None:
        return https_fn.Response(
            status=400,
            headers={
                "Content-Type": "application/json",
            },
            content_type="application/json",
            response=json.dumps({
                "error": "No firestore data",
            },)
        )

    # save latest firestore data
    save_latest_firestore_data(main_data.firestore_data, telegram_id)
    if (main_data.firestore_data.is_expired and main_data.firestore_data.is_sent == False):
        user_id = telegram_id if telegram_id is not None else "747213289"
        set_is_sent(user_id, True)
        send_message_telegram(
            telegram_id=user_id,
            message='Token expired' + '\n' +
            'php_session_id: ' + main_data.new_php_session_id)
    elif (main_data.available_dates != []):
        send_message_telegram(
            telegram_id=telegram_id if telegram_id is not None else "747213289",
            message='php_session_id: ' +
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
            "is_sent": main_data.firestore_data.is_sent,
            "available_dates": main_data.available_dates,
            "full_capacity_dates": main_data.full_capacity_dates,
            "offDates_dates": main_data.offDates_dates,
            "blocked_dates": main_data.blocked_dates,
        },)

    )


def get_main_data(input_php_session_id: str | None, telegram_id: str) -> MainData | None:
    is_sent = False
    php_session_id = None
    url = None
    if (input_php_session_id is None):
        firestore_data = get_latest_firestore_data(telegram_id=telegram_id)
        if firestore_data is None:
            return None
        is_sent = firestore_data.is_sent
        php_session_id = firestore_data.php_session_id
        url = firestore_data.url
    else:
        php_session_id = input_php_session_id

    # Cookies
    cookies = {
        "PHPSESSID": php_session_id,
    }
    url = APPOINTMENT_URL if url is None else url

    # Send the GET request with cookies
    response = requests.get(url, cookies=cookies)

    # Check if the response contains HTML content
    if "text/html" in response.headers.get("content-type", "").lower():
        # Check if it contains the expected HTML content and not the script
        if "<!DOCTYPE html>" in response.text and \
                "<script>\n\tdocument.location.href='book_appointment.php'\n</script>" not in response.text:
            print("Valid HTML content found in response.")
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
            result = MainData(old_php_session_id=php_session_id,
                              new_php_session_id=new_php_session_id,
                              blocked_dates=blocked_dates,
                              available_dates=available_dates,
                              full_capacity_dates=full_capacity_dates,
                              offDates_dates=offDates_dates,
                              firestore_data=FirestoreData(
                                  php_session_id=new_php_session_id,
                                  current_date=datetime.now()
                              )
                              )
            return result
        else:
            print("HTML content does not match expectations.")
    else:
        print("No HTML content found in response.")

    return MainData(old_php_session_id=php_session_id,
                    new_php_session_id=php_session_id,
                    blocked_dates=[],
                    available_dates=[],
                    full_capacity_dates=[],
                    offDates_dates=[],
                    firestore_data=FirestoreData(
                        php_session_id=php_session_id,
                        current_date=datetime.now(),
                        is_expired=True,
                        is_sent=is_sent
                    )
                    )
