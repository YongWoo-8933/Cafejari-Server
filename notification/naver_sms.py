import json

import requests

from cafejari.settings import ADMIN_PHONE_NUMBER_LIST, NHN_SMS_APP_KEY, NHN_SMS_SECRET_KEY, NHN_SMS_CALLING_NUMBER


def send_sms_to_admin(content):
    for number in ADMIN_PHONE_NUMBER_LIST:
        requests.post(
            f"https://api-sms.cloud.toast.com/sms/v3.0/appKeys/{NHN_SMS_APP_KEY}/sender/sms",
            headers={
                'Content-Type': 'application/json',
                "X-Secret-Key": NHN_SMS_SECRET_KEY
            },
            data=json.dumps({
                "sendNo": NHN_SMS_CALLING_NUMBER,
                "body": content,
                "recipientList": [
                    {
                        "recipientNo": number,
                        "countryCode": "82"
                    }
                ],
            }),
        )