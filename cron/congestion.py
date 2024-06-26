import logging
import time

import requests

from cafe.models import CongestionArea
from cafe.serializers import CongestionAreaSerializer
from cafejari.settings import SEOUL_CITY_DATA_API_KEY

def update_congestion_area():
    try:
        congestion_area_list = CongestionArea.objects.all()
        for congestion_area in congestion_area_list:
            url = f"http://openapi.seoul.go.kr:8088/{SEOUL_CITY_DATA_API_KEY}/json/citydata_ppltn/1/5/{congestion_area.name}"
            response = requests.get(url=url)

            if response.status_code == 200:
                congestion = response.json()['SeoulRtd.citydata_ppltn'][0]['AREA_CONGEST_LVL']
                serializer = CongestionAreaSerializer(congestion_area, data={"current_congestion": congestion},
                                                      partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()

            time.sleep(0.1)
    except Exception as e:
        logger = logging.getLogger('my')
        logger.error(e)