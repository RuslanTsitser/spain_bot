
from datetime import datetime

from const.key import APPOINTMENT_URL


class FirestoreData:
    def __init__(self, php_session_id: str, current_date: datetime, url: str, is_expired: bool = False, is_sent: bool = False,):
        self.php_session_id = php_session_id
        self.url = url
        self.current_date = current_date
        self.is_expired = is_expired
        self.is_sent = is_sent

    def __str__(self):
        return f"php_session_id: {self.php_session_id}\ncurrent_date: {self.current_date}\nis_expired: {self.is_expired}\nis_sent: {self.is_sent}\nurl: {self.url}"

    def __repr__(self):
        return f"php_session_id: {self.php_session_id}\ncurrent_date: {self.current_date}\nis_expired: {self.is_expired}\nis_sent: {self.is_sent}\nurl: {self.url}"

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
