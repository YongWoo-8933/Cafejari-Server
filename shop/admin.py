from django.contrib import admin
from django.utils.html import format_html

from cafe.models import Brand
from shop.models import Item, Gifticon, Coupon, UserCoupon
from utils import ImageModelAdmin


class BrandInline(admin.TabularInline):
    model = Brand


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "image_tag", "brand_name", "price",)
    list_filter = ("brand__name",)
    search_fields = ("brand__name", "name",)
    ordering = ("brand__name", "name",)
    list_select_related = ["brand",]
    save_as = True
    preserve_filters = True

    def image_tag(self, item):
        return format_html('<img src="{}" width="85" height="85" />', item.small_image_url) if item.small_image_url else None

    def brand_name(self, item):
        return item.brand.name if item.brand else None

    image_tag.short_description = "이미지"
    brand_name.short_description = "브랜드"


@admin.register(Gifticon)
class GifticonAdmin(ImageModelAdmin):
    list_display = ("id", "item_name", "user_nickname", 'image_tag', "expiration_period", "is_used",)
    list_filter = ("user__profile__nickname", "item__name", "is_used")
    search_fields = ("user__profile__nickname", "item__name",)
    ordering = ("expiration_period", "is_used",)
    date_hierarchy = "expiration_period"
    list_select_related = ["item", "user"]
    save_as = True
    preserve_filters = True

    def image_tag(self, gifticon):
        return format_html('<img src="{}" width="85" height="85" />', gifticon.image.url) if gifticon.image else None

    def item_name(self, gifticon):
        return gifticon.item.name if gifticon.item else None

    def user_nickname(self, gifticon):
        return gifticon.user.profile.nickname if gifticon.user else None

    image_tag.short_description = "이미지 이름"
    item_name.short_description = "아이템 이름"
    user_nickname.short_description = "닉네임"


@admin.register(Coupon)
class CouponAdmin(ImageModelAdmin):
    list_display = ("id", "name", "image_tag", "description",)
    search_fields = ("name",)
    ordering = ("name",)
    save_as = True
    preserve_filters = True

    def image_tag(self, coupon):
        return format_html('<img src="{}" width="85" height="85" />', coupon.image.url) if coupon.image else None

    image_tag.short_description = "이미지"


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = ("id", "coupon_name", "user_nickname", "expiration_period", "is_used",)
    list_filter = ("user__profile__nickname", "coupon__name", "is_used")
    search_fields = ("user__profile__nickname", "item__name",)
    ordering = ("expiration_period", "is_used",)
    date_hierarchy = "expiration_period"
    list_select_related = ["coupon", "user"]
    save_as = True
    preserve_filters = True

    def coupon_name(self, user_coupon): return user_coupon.coupon.name

    def user_nickname(self, user_coupon): return user_coupon.user.profile.nickname

    coupon_name.short_description = "쿠폰 이름"
    user_nickname.short_description = "닉네임"
