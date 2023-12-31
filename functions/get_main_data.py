from datetime import datetime

import re
import requests
from classes import FirestoreData, FirestoreDataWithDates, MainData
from app_firestore import get_latest_firestore_data, save_latest_firestore_data
from const.key import APPOINTMENT_URL

# Fetch main data from the website using the PHPSESSID cookie


def fetch_data_from_website(
    php_session_id: str,
    url: str,
    is_sent: bool = False,
) -> FirestoreDataWithDates:
    # Cookies
    cookies = {
        "PHPSESSID": php_session_id,
    }
    print(f"PHPSESSID value: {php_session_id}")
    print(f"URL value: {url}")
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

            return FirestoreDataWithDates(
                php_session_id=new_php_session_id,
                current_date=datetime.now(),
                is_expired=False,
                is_sent=is_sent,
                url=url,
                blocked_dates=blocked_dates,
                available_dates=available_dates,
                full_capacity_dates=full_capacity_dates,
                offDates_dates=offDates_dates,
            )
    return FirestoreDataWithDates(
        php_session_id=php_session_id,
        current_date=datetime.now(),
        is_expired=True,
        is_sent=is_sent,
        url=url,
        blocked_dates=[],
        available_dates=[],
        full_capacity_dates=[],
        offDates_dates=[],
    )


# Get main data from the website using FirestoreData
def get_main_data_from_db(firestore_data: FirestoreData,
                          is_sent: bool = False
                          ) -> MainData:
    php_session_id = firestore_data.php_session_id
    url = firestore_data.url

    firestore_data = fetch_data_from_website(php_session_id, url, is_sent)

    return MainData(
        old_php_session_id=php_session_id,
        new_php_session_id=firestore_data.php_session_id,
        blocked_dates=firestore_data.blocked_dates,
        available_dates=firestore_data.available_dates,
        full_capacity_dates=firestore_data.full_capacity_dates,
        offDates_dates=firestore_data.offDates_dates,
        firestore_data=firestore_data,
    )


# Get main data from the website using FirestoreData found by telegram_id or request_php_token and url
def get_main_data(
    request_php_token: str | None,
    url: str | None,
    telegram_id: str,
) -> MainData | None:

    firestore_data = get_latest_firestore_data(telegram_id)
    if firestore_data is None:
        if (request_php_token is not None):
            url = url if url is not None else APPOINTMENT_URL
            firestore_data = fetch_data_from_website(request_php_token, url)
            save_latest_firestore_data(firestore_data, telegram_id)
            return get_main_data_from_db(firestore_data)
        else:
            return None

    if (request_php_token is not None):
        firestore_data.php_session_id = request_php_token

    if (url is not None):
        firestore_data.url = url

    main_data = get_main_data_from_db(firestore_data)

    firestore_data = main_data.firestore_data
    # save latest firestore data
    save_latest_firestore_data(firestore_data, telegram_id)
    return main_data
