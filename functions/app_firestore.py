from firebase_admin import firestore, initialize_app

from classes import FirestoreData

initialize_app()

# get latest firestore data


def get_latest_firestore_data(telegram_id: str | None) -> FirestoreData | None:
    telegram_id = telegram_id if telegram_id is not None else "latest"
    print("get latest firestore data")
    db = firestore.client()
    doc_ref = db.collection(u'php_session_id').document(telegram_id)
    doc = doc_ref.get()
    if doc.exists:
        return FirestoreData(
            php_session_id=doc.to_dict()["php_session_id"],
            current_date=doc.to_dict()["current_date"],
            is_expired=doc.to_dict()["is_expired"],
            is_sent=doc.to_dict()["is_sent"]
        )
    else:
        print(u'No such document!')
        return None

# save latest firestore data


def save_latest_firestore_data(firestore_data: FirestoreData, telegram_id: str | None) -> None:
    telegram_id = telegram_id if telegram_id is not None else "latest"
    db = firestore.client()
    doc_ref = db.collection(u'php_session_id').document(telegram_id)
    doc_ref.set({
        u'php_session_id': firestore_data.php_session_id,
        u'current_date': firestore_data.current_date,
        u'is_expired': firestore_data.is_expired,
        u'is_sent': firestore_data.is_sent,
    })
    print("saved latest firestore data")
