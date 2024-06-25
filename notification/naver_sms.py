import json

import requests

from cafejari.settings import ADMIN_PHONE_NUMBER_LIST, NAVER_SMS_CALLING_NUMBER, A_PICK_API_KEY


def send_sms_to_admin(content):
    for number in ADMIN_PHONE_NUMBER_LIST:
        requests.post(
            "https://apick.app/rest/send_sms",
            headers={
                'Content-Type': 'application/json',
                "CL_AUTH_KEY": A_PICK_API_KEY,
            },
            data=json.dumps({
                "from": NAVER_SMS_CALLING_NUMBER,
                "to": number,
                "text": content
            }),
        )