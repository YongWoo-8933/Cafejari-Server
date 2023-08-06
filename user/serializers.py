
from rest_framework import serializers

from user.models import User, Profile, Grade, ProfileImage, NicknameAdjective, NicknameNoun

# 기본 serializer ----------------------------------------------------------------------------
from utils import ImageModelSerializer


class GradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grade
        fields = "__all__"


class ProfileImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileImage
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ['password']


class NicknameAdjectiveSerializer(serializers.ModelSerializer):

    class Meta:
        model = NicknameAdjective
        fields = "__all__"


class NicknameNounSerializer(serializers.ModelSerializer):

    class Meta:
        model = NicknameNoun
        fields = "__all__"



# 응용 serializer ----------------------------------------------------------------------------
# grade image 저장용 serializer
class GradeResponseSerializer(ImageModelSerializer):

    class Meta:
        model = Grade
        fields = "__all__"


# profile_image image 저장용 serializer
class ProfileImageResponseSerializer(ImageModelSerializer):

    class Meta:
        model = ProfileImage
        fields = "__all__"


class PartialProfileSerializer(serializers.ModelSerializer):
    grade = GradeResponseSerializer(read_only=True)
    profile_image = ProfileImageResponseSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['grade'] = GradeResponseSerializer(read_only=True)
        self.fields['profile_image'] = ProfileImageResponseSerializer(read_only=True)
        return super(PartialProfileSerializer, self).to_representation(instance)

    class Meta:
        model = Profile
        fields = ["id", "nickname", "grade", "profile_image"]


class PartialUserSerializer(serializers.ModelSerializer):
    profile = PartialProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", 'profile', 'date_joined']


class ProfileResponseSerializer(ProfileSerializer):
    grade = GradeResponseSerializer(read_only=True)
    profile_image = ProfileImageResponseSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['grade'] = GradeResponseSerializer(read_only=True)
        self.fields['profile_image'] = ProfileImageResponseSerializer(read_only=True)
        return super(ProfileResponseSerializer, self).to_representation(instance)


class UserResponseSerializer(UserSerializer):
    profile = ProfileResponseSerializer(read_only=True)




