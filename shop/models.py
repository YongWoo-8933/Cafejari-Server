from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=63)
    code = models.CharField(max_length=31, unique=True)
    price = models.IntegerField()
    description = models.TextField(null=True, default=None, blank=True)
    small_image_url = models.URLField(max_length=255)
    large_image_url = models.URLField(max_length=255)
    limit_day = models.IntegerField(default=30)
    brand = models.ForeignKey(
        "cafe.Brand",
        on_delete=models.SET_NULL,
        related_name="item",
        db_column="brand",
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'shop_item'
        db_table_comment = '아이템 모델'
        app_label = 'shop'
        ordering = ['brand__name', 'name']
        indexes = [
            models.Index(fields=["name"], name="item_name_index"),
            models.Index(fields=["code"], name="item_code_index"),
        ]


def gifticon_image_upload_path(instance, filename):
    return f"shop/gifticon/{instance.expiration_period.year}/{instance.expiration_period.month}/{instance.expiration_period.day}/{filename}"


class Gifticon(models.Model):
    image = models.ImageField(upload_to=gifticon_image_upload_path)
    tr_id = models.CharField(max_length=31)
    expiration_period = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    item = models.ForeignKey(
        "Item",
        on_delete=models.SET_NULL,
        related_name="gifticon",
        db_column="item",
        default=None,
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="gifticon",
        db_column="user",
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'shop_gifticon'
        db_table_comment = '기프티콘 모델'
        app_label = 'shop'
        ordering = ['expiration_period']
        indexes = [
            models.Index(fields=["expiration_period"], name="gifticon_period_index"),
        ]


def coupon_image_upload_path(instance, filename):
    return f"shop/coupon/{instance.name}_{filename}"


class Coupon(models.Model):
    name = models.CharField(max_length=31, unique=True)
    description = models.TextField(null=True, default=None, blank=True)
    image = models.ImageField(upload_to=coupon_image_upload_path)

    class Meta:
        db_table = 'shop_coupon'
        db_table_comment = '쿠폰 모델'
        app_label = 'shop'
        ordering = ['name']


class UserCoupon(models.Model):
    is_used = models.BooleanField(default=False)
    expiration_period = models.DateTimeField(null=True, blank=True, default=None)
    coupon = models.ForeignKey(
        "Coupon",
        on_delete=models.CASCADE,
        related_name="user_coupon",
        db_column="coupon",
    )
    user = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        related_name="user_coupon",
        db_column="user",
    )

    class Meta:
        db_table = 'shop_user_coupon'
        db_table_comment = '유저에게 배포된 쿠폰'
        app_label = 'shop'
        ordering = ['expiration_period', 'user__username']
