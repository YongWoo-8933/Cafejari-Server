
from rest_framework import serializers

from user.models import User, Profile, Grade, ProfileImage


# 기본 serializer ----------------------------------------------------------------------------
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



# 응용 serializer ----------------------------------------------------------------------------
class PartialProfileSerializer(serializers.ModelSerializer):
    grade = GradeSerializer(read_only=True)
    profile_image = ProfileImageSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['grade'] = GradeSerializer(read_only=True)
        self.fields['profile_image'] = ProfileImageSerializer(read_only=True)
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
    grade = GradeSerializer(read_only=True)
    profile_image = ProfileImageSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['grade'] = GradeSerializer(read_only=True)
        self.fields['profile_image'] = ProfileImageSerializer(read_only=True)
        return super(ProfileResponseSerializer, self).to_representation(instance)


class UserResponseSerializer(UserSerializer):
    profile = ProfileResponseSerializer(read_only=True)




