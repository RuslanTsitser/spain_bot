# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

import json
from firebase_functions import scheduler_fn, https_fn

from app_firestore import get_latest_firestore_data, save_latest_firestore_data
from app_telegram_bot import send_message_telegram
from app_firestore import get_list_of_documents_ids
from app_firestore import set_is_sent
from get_main_data import get_main_data


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
        main_data = get_main_data(firestore_data)
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
                main_data.new_php_session_id + '\n' + 'available_dates: ' +
                str(main_data.available_dates) + '\n' +
                'url: ' + firestore_data.url
            )


@https_fn.on_request()
def handle(request: https_fn.Request) -> https_fn.Response:
    request_php_token = request.args.get("php_token")
    telegram_id = request.args.get("telegram_id")
    url = request.args.get("url")

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
    firestore_data = get_latest_firestore_data(telegram_id)
    if firestore_data is None:
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
    if (request_php_token is not None):
        firestore_data.php_session_id = request_php_token

    if (url is not None):
        firestore_data.url = url

    main_data = get_main_data(firestore_data)

    firestore_data = main_data.firestore_data
    # save latest firestore data
    save_latest_firestore_data(firestore_data, telegram_id)
    if (main_data.firestore_data.is_expired):
        send_message_telegram(
            telegram_id=telegram_id,
            message='Token expired' + '\n' +
            'php_session_id: ' + main_data.new_php_session_id)
    else:
        send_message_telegram(
            telegram_id=telegram_id,
            message='php_session_id: ' +
            main_data.new_php_session_id + '\n' + 'available_dates: ' +
            str(main_data.available_dates) + '\n' +
            'url: ' + firestore_data.url
        )

    # return response in json format
    return https_fn.Response(
        status=200,
        headers={
            "Content-Type": "application/json",
        },
        content_type="application/json",
        response=json.dumps({
            "url": main_data.firestore_data.url,
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
