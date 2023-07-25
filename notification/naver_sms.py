import base64
import hashlib
import hmac
import json
import time

import requests

from cafejari.settings import ADMIN_PHONE_NUMBER_LIST, NAVER_SERVICE_ID, NAVER_API_ID, NAVER_SMS_CALLING_NUMBER, \
    NAVER_API_SECRET


def send_sms_to_admin(content):
    for number in ADMIN_PHONE_NUMBER_LIST:
        requests.post(
            f"https://sens.apigw.ntruss.com/sms/v2/services/{NAVER_SERVICE_ID}/messages",
            headers={
                'Content-Type': 'application/json',
                "x-ncp-apigw-timestamp": str(int(time.time() * 1000)),
                "x-ncp-iam-access-key": NAVER_API_ID,
                "x-ncp-apigw-signature-v2": make_signature("POST")
            },
            data=json.dumps({
                "type": "SMS",
                "contentType": "COMM",
                "countryCode": "82",
                "from": NAVER_SMS_CALLING_NUMBER,
                "content": content,
                "messages": [{"to": number}]
            }),
        )


def make_signature(method):
    timestamp = str(int(time.time() * 1000))
    method = method
    uri = f"/sms/v2/services/{NAVER_SERVICE_ID}/messages"
    message = method + " " + uri + "\n" + timestamp + "\n" + NAVER_API_ID
    message = bytes(message, 'UTF-8')
    signing_key = base64.b64encode(hmac.new(bytes(NAVER_API_SECRET, 'UTF-8'), message, digestmod=hashlib.sha256).digest())
    return signing_key