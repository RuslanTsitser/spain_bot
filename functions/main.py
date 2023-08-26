# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from datetime import datetime
import json
from firebase_functions import scheduler_fn, https_fn
from firebase_admin import firestore, initialize_app
import requests
import re
from telebot import TeleBot

initialize_app()


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
                "error": "Token expired",
            },)
        )

    # save latest firestore data
    save_latest_firestore_data(main_data.firestore_data)
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
            "available_dates": main_data.available_dates,
            "full_capacity_dates": main_data.full_capacity_dates,
            "offDates_dates": main_data.offDates_dates,
            "blocked_dates": main_data.blocked_dates,
        },)

    )


# URL to request
url = "https://blsspain-russia.com/moscow/english/appointment.php"


class FirestoreData:
    def __init__(self, php_session_id: str, current_date: datetime):
        self.php_session_id = php_session_id
        self.current_date = current_date

    def __str__(self):
        return f"php_session_id: {self.php_session_id}\ncurrent_date: {self.current_date}"

    def __repr__(self):
        return f"php_session_id: {self.php_session_id}\ncurrent_date: {self.current_date}"

# class that contain fields: old_php_session_id, new_php_session_id, blocked_dates, available_dates, full_capacity_dates, offDates_dates as not


class MainData:
    def __init__(self, old_php_session_id: str, new_php_session_id: str, blocked_dates: list, available_dates: list, full_capacity_dates: list, offDates_dates: list, firestore_data: FirestoreData):
        self.old_php_session_id = old_php_session_id
        self.new_php_session_id = new_php_session_id
        self.blocked_dates = blocked_dates
        self.available_dates = available_dates
        self.full_capacity_dates = full_capacity_dates
        self.offDates_dates = offDates_dates
        self.firestore_data = firestore_data

    def __str__(self):
        return f"old_php_session_id: {self.old_php_session_id}\nnew_php_session_id: {self.new_php_session_id}\nblocked_dates: {self.blocked_dates}\navailable_dates: {self.available_dates}\nfull_capacity_dates: {self.full_capacity_dates}\noffDates_dates: {self.offDates_dates}\n{self.firestore_data}"

    def __repr__(self):
        return f"old_php_session_id: {self.old_php_session_id}\nnew_php_session_id: {self.new_php_session_id}\nblocked_dates: {self.blocked_dates}\navailable_dates: {self.available_dates}\nfull_capacity_dates: {self.full_capacity_dates}\noffDates_dates: {self.offDates_dates}\n{self.firestore_data}"


def get_php_session_id(php_session_id: str) -> MainData | None:
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
            return None
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


# get latest firestore data
def get_latest_firestore_data() -> FirestoreData | None:
    print("get latest firestore data")
    db = firestore.client()
    doc_ref = db.collection(u'php_session_id').document(u'latest')
    doc = doc_ref.get()
    if doc.exists:
        return FirestoreData(
            php_session_id=doc.to_dict()["php_session_id"],
            current_date=doc.to_dict()["current_date"],
        )
    else:
        print(u'No such document!')
        return None

# save latest firestore data


def save_latest_firestore_data(firestore_data: FirestoreData) -> None:
    db = firestore.client()
    doc_ref = db.collection(u'php_session_id').document(u'latest')
    doc_ref.set({
        u'php_session_id': firestore_data.php_session_id,
        u'current_date': firestore_data.current_date,
    })
    print("saved latest firestore data")


def send_message_telegram(message: str) -> None:
    bot = TeleBot("5878623665:AAHSivBGwtr3LA2zehj65WqbKPfs_rT9wnE")
    bot.send_message("747213289", message)
    print("send message telegram")


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
