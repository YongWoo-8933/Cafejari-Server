
from rest_framework import serializers

from cafe.serializers import CafeSerializer
from request.models import CafeAdditionRequest, CafeInformationSuggestion, WithdrawalRequest, UserMigrationRequest, \
    AppFeedback

# 기본 serializer ------------------------------------------------------------------------------------


class CafeAdditionRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = CafeAdditionRequest
        fields = "__all__"


class CafeInformationSuggestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CafeInformationSuggestion
        fields = "__all__"


class WithdrawalRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = WithdrawalRequest
        fields = "__all__"


class UserMigrationRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMigrationRequest
        fields = "__all__"


class AppFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppFeedback
        fields = "__all__"




# 응용 serializer ------------------------------------------------------------------------------------
class CafeAdditionRequestResponseSerializer(CafeAdditionRequestSerializer):
    cafe = CafeSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['cafe'] = CafeSerializer(read_only=True)
        return super(CafeAdditionRequestResponseSerializer, self).to_representation(instance)


class CafeInformationSuggestionRequestResponseSerializer(CafeInformationSuggestionSerializer):
    cafe = CafeSerializer(read_only=True)
    suggested_cafe = CafeSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['cafe'] = CafeSerializer(read_only=True)
        return super(CafeInformationSuggestionSerializer, self).to_representation(instance)
