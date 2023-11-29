import logging
import os
import time

import requests
from django.core.files.base import ContentFile

from cafe.models import Brand
from cafe.serializers import BrandSerializer
from shop.giftishow_biz import GiftishowBiz
from shop.models import Item
from shop.serializers import ItemSerializer

def update_item_list():
    try:
        response = GiftishowBiz.get_items()
        brand_name_set = set()
        brand_exclude_set = {"잠바주스", "스무디킹"}

        if response:
            if response.status_code == 200:
                goods = response.json()['result']['goodsList']
                # 브랜드 세팅
                for good in goods:
                    goods_type = good['goodsTypeDtlNm']
                    sale_state = good['goodsStateCd']
                    if sale_state == "SALE" and goods_type == "커피/음료":
                        brand_name = good['brandName']
                        if brand_name not in brand_name_set and brand_name not in brand_exclude_set:
                            brand_image_url = good['brandIconImg']
                            response = requests.get(brand_image_url, stream=True)
                            temp_file_name = f"{brand_name}_로고_이미지.jpg"
                            if response.status_code == 200:
                                with open(temp_file_name, 'wb') as file:
                                    for chunk in response.iter_content(1024):
                                        file.write(chunk)
                            time.sleep(0.4)
                            with open(temp_file_name, 'rb') as f:
                                image = ContentFile(f.read(), name=temp_file_name)
                            try:
                                brand = Brand.objects.get(name=brand_name)
                                brand_serializer = BrandSerializer(brand, data={"image": image, "has_item": True}, partial=True)
                            except Brand.DoesNotExist:
                                brand_serializer = BrandSerializer(data={"name": brand_name, "image": image, "has_item": True}, partial=True)
                            brand_serializer.is_valid(raise_exception=True)
                            brand_serializer.save()
                            brand_name_set.add(brand_name)
                            os.remove(temp_file_name)
                # 아이템 세팅
                for good in goods:
                    type = good['goodsTypeDtlNm']
                    sale_state = good['goodsStateCd']
                    brand = good['brandName']
                    price = int(good['realPrice'])
                    if sale_state == "SALE" and type == "커피/음료" and brand not in brand_exclude_set and 1500 < price < 31000:
                        code = good['goodsCode']
                        data = {
                            "code": code, "name": good['goodsName'], "description": good['content'],
                            "small_image_url": good['goodsImgS'], "large_image_url": good['goodsImgB'],
                            "limit_day": good['limitDay'], "brand": Brand.objects.get(name=brand).id,
                            "price": round(price * 1.3 / 100) * 100
                        }
                        try:
                            item = Item.objects.get(code=code)
                            item_serializer = ItemSerializer(item, data=data, partial=True)
                        except Item.DoesNotExist:
                            item_serializer = ItemSerializer(data=data)
                        item_serializer.is_valid(raise_exception=True)
                        item_serializer.save()
                logger = logging.getLogger('my')
                logger.info("item updated")
    except Exception as e:
        logger = logging.getLogger('my')
        logger.error(e)