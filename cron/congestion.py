import time

import requests

from cafe.models import CongestionArea
from cafe.serializers import CongestionAreaSerializer
from cafejari.settings import SEOUL_CITY_DATA_API_KEY


def update_congestion_area():
    congestion_area_list = CongestionArea.objects.all()
    for congestion_area in congestion_area_list:
        url = f"http://openapi.seoul.go.kr:8088/{SEOUL_CITY_DATA_API_KEY}/json/citydata_ppltn/1/5/{congestion_area.name}"
        response = requests.get(url=url)

        if response.status_code == 200:
            try:
                congestion = response.json()['SeoulRtd.citydata_ppltn'][0]['AREA_CONGEST_LVL']
                serializer = CongestionAreaSerializer(congestion_area, data={"current_congestion": congestion},
                                                      partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except KeyError:
                print(f"congestion 읽기 실패 ({congestion_area.name})")
        else:
            print("congestion 통신 실패")

        time.sleep(0.1)