import datetime

import pytz
import requests

from cafejari.settings import GIFTISHOW_AUTH_CODE, GIFTISHOW_AUTH_TOKEN, GIFTISHOW_USER_ID, ADMIN_PHONE_NUMBER_LIST


class GiftishowBiz:
    base_url = "https://bizapi.giftishow.com/bizApi"
    base_params = {
        "custom_auth_code": GIFTISHOW_AUTH_CODE,
        "custom_auth_token": GIFTISHOW_AUTH_TOKEN,
        "dev_yn": "N",
    }
    base_datetime = datetime.datetime(year=2023, month=1, day=1, hour=0, minute=0, second=1, tzinfo=pytz.UTC)

    @classmethod
    def __generate_tr_id(cls):
        now = datetime.datetime.now(tz=pytz.UTC)
        seconds = (now - cls.base_datetime).total_seconds()
        return f"cafejari_{int(seconds)}"

    @classmethod
    def get_items(cls):
        url = cls.base_url + "/goods"
        params = cls.base_params.copy()
        params.update({
            "api_code": "0101",
            "start": "1",
            "size": "5000",
        })
        try:
            response = requests.post(url=url, params=params)
        except requests.Timeout:
            response = None
        except requests.RequestException:
            response = None
        return response

    @classmethod
    def send_gifticon(cls, goods_code):
        tr_id = cls.__generate_tr_id()
        url = cls.base_url + "/send"
        params = cls.base_params.copy()
        params.update({
            "api_code": "0204",
            "goods_code": str(goods_code),
            "mms_msg": "유효기간 내에 사용해주세요. 기간 연장은 불가합니다.",
            "mms_title": "카페자리 상품구매",
            "callback_no": ADMIN_PHONE_NUMBER_LIST[0],
            "phone_no": ADMIN_PHONE_NUMBER_LIST[0],
            "tr_id": tr_id,
            "user_id": GIFTISHOW_USER_ID,
            "gubun": "I"
        })
        try:
            response = requests.post(url=url, params=params,  timeout=15)
        except requests.Timeout:
            # 타임 아웃시 쿠폰 취소 요청 발송
            cls.cancel_gifticon(tr_id=tr_id)
            response = None
        except requests.RequestException:
            response = None

        return tr_id, response

    @classmethod
    def cancel_gifticon(cls, tr_id):
        url = cls.base_url + "/cancel"
        params = cls.base_params.copy()
        params.update({
            "api_code": "0202",
            "tr_id": tr_id,
            "user_id": GIFTISHOW_USER_ID,
        })
        try:
            response = requests.post(url=url, params=params, timeout=15)
        except requests.Timeout:
            # 타임아웃 쿠폰 취소 요청 발송
            response = None
        except requests.RequestException:
            response = None

        return response

    @classmethod
    def get_biz_money_balance(cls):
        url = cls.base_url + "/bizmoney"
        params = cls.base_params.copy()
        params.update({
            "api_code": "0301",
            "user_id": GIFTISHOW_USER_ID,
        })
        try:
            response = requests.post(url=url, params=params, timeout=15)
            return int(response.json()["result"]["balance"])
        except requests.Timeout:
            # 타임아웃 쿠폰 취소 요청 발송
            response = None
        except requests.RequestException:
            response = None

        return response