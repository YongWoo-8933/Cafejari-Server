from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models


def grade_image_upload_path(instance, filename):
    return f"user/grade/{instance.name}_등급_{filename}"


class Grade(models.Model):
    step = models.IntegerField(unique=True)  # 각 등급의 레벨(단계)
    name = models.CharField(max_length=31, unique=True)
    description = models.TextField(null=True, default=None, blank=True)
    image = models.ImageField(upload_to=grade_image_upload_path, blank=True, null=True, default=None)
    sharing_count_requirement = models.IntegerField()  # 해당 등급 진입에 필요한 요구 공유 횟수
    sharing_restriction_per_cafe = models.IntegerField()  # 카페당 포인트 받으며 공유할 수 있는 횟수
    activity_stack_restriction_per_day = models.IntegerField()  # 하루에 포인트 받으며 활동할 수 있는 카페 수

    class Meta:
        db_table = 'user_grade'
        db_table_comment = '유저 등급'
        app_label = 'user'
        ordering = ['step', 'name']


class User(AbstractUser):
    username = models.CharField(max_length=15, null=True, blank=True, default=None)
    email = models.EmailField(max_length=63, unique=False, null=True, blank=True, default=None)

    class Meta:
        db_table = 'user_user'
        db_table_comment = '유저'
        app_label = 'user'
        ordering = ['-date_joined']


def profile_image_upload_path(instance, filename):
    if instance.is_default:
        return f"user/profile/기본_프로필사진_{filename}"
    else:
        return f"user/profile/개인_프로필사진_{filename}"


class ProfileImage(models.Model):
    is_default = models.BooleanField(default=True)
    image = models.ImageField(upload_to=profile_image_upload_path)

    class Meta:
        db_table = 'user_profile_image'
        db_table_comment = '유저 프로필 이미지 모델'
        app_label = 'user'


class Gender(Enum):
    male = 0
    female = 1


class AgeRange(Enum):
    ZeroToNine = "0~9"
    TemToNineteen = "10~19"
    TwentyToTwentyNine = "20~29"
    ThirtyToThirtyNine = "30~39"
    FortyToFortyNine = "40~49"
    FiftyToFiftyNine = "50~59"
    SixtyToSixtyNine = "60~69"
    SeventyToSeventyNine = "70~79"
    EightyToEightyNine = "80~89"
    NinetyAbove = "90~"


class Profile(models.Model):
    nickname = models.CharField(max_length=15, unique=True)
    gender = models.IntegerField(choices=((Gender.male.value, '남성'), (Gender.female.value, '여성'),), null=True, default=None, blank=True)
    age_range = models.CharField(max_length=15, choices=((age_range.value, age_range.value) for age_range in AgeRange), null=True, default=None, blank=True)
    date_of_birth = models.CharField(max_length=4, null=True, default=None, blank=True)
    phone_number = models.CharField(max_length=8, null=True, default=None, blank=True) # 010뒤 8자리
    point = models.IntegerField(default=0)
    marketing_push_enabled = models.BooleanField(default=False)
    occupancy_push_enabled = models.BooleanField(default=True)
    log_push_enabled = models.BooleanField(default=True)
    fcm_token = models.CharField(max_length=255, null=True, default=None, blank=True)
    grade = models.ForeignKey(
        "Grade",
        on_delete=models.SET_NULL,
        related_name="profile",
        db_column="grade",
        blank=True,
        null=True
    )
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name="profile",
        db_column="user"
    )
    profile_image = models.ForeignKey(
        'ProfileImage',
        on_delete=models.SET_NULL,
        related_name="profile",
        db_column="profile_image",
        default=None,
        blank=True,
        null=True
    )
    favorite_cafe = models.ManyToManyField(
        'cafe.Cafe',
        related_name='user',
        db_column="favorite_cafe",
        blank=True
    )

    class Meta:
        db_table = 'user_profile'
        db_table_comment = '프로필'
        app_label = 'user'
        ordering = ['-user__date_joined']


class NicknameAdjective(models.Model):
    value = models.CharField(max_length=4, unique=True)
    length = models.IntegerField()
    update = models.DateTimeField(auto_now_add=True),

    class Meta:
        db_table = 'user_nickname_adjective'
        db_table_comment = '닉네임 자동생성 형용사 후보'
        app_label = 'user'
        ordering = ['length', 'value']


class NounType(Enum):
    Coffee = "커피"
    Latte = "라떼"
    NoneCoffee = "논커피"
    Tea = "티"
    dessert = "디저트"


class NicknameNoun(models.Model):
    value = models.CharField(max_length=5, unique=True)
    type = models.CharField(choices=((noun_type.value, noun_type.value) for noun_type in NounType))
    update = models.DateTimeField(auto_now_add=True),

    class Meta:
        db_table = 'user_nickname_noun'
        db_table_comment = '닉네임 자동생성 명사 후보'
        app_label = 'user'
        ordering = ['type', 'value']
