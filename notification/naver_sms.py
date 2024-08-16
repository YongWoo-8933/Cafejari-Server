import logging

import boto3

from cafejari.settings import ADMIN_PHONE_NUMBER_LIST, AWS_SMS_ACCESS_KEY, \
    AWS_SMS_SECRET_KEY, AWS_SMS_REGION_NAME


def send_sms_to_admin(content):
    try:
        client = boto3.client(
            "sns",
            aws_access_key_id=AWS_SMS_ACCESS_KEY,
            aws_secret_access_key=AWS_SMS_SECRET_KEY,
            region_name=AWS_SMS_REGION_NAME,
        )
        for number in ADMIN_PHONE_NUMBER_LIST:
            client.publish(
                PhoneNumber="+82" + number[1:],
                Message=content
            )
    except Exception as e:
        logger = logging.getLogger('my')
        logger.error(e)