
from rest_framework import serializers

from challenge.models import Challenge, ChallengeMilestone, Challenger, ChallengePoint


# 기본 serializer ------------------------------------------------------------
from utils import ImageModelSerializer


# 기본 serializer ------------------------------------------------------------
class ChallengeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenge
        fields = "__all__"


class ChallengeMilestoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChallengeMilestone
        fields = "__all__"


class ChallengerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Challenger
        fields = "__all__"


class ChallengePointSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChallengePoint
        fields = "__all__"



# 응용 serializer ------------------------------------------------------------
# 챌린저 응답용 serializer
class ChallengerResponseSerializer(ChallengerSerializer):
    challenge = ChallengeSerializer(read_only=True)
    challenge_point = ChallengePointSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        self.fields['challenge'] = ChallengeSerializer(read_only=True)
        return super(ChallengerResponseSerializer, self).to_representation(instance)


# 챌린지 응답용 serializer
class ChallengeResponseSerializer(ImageModelSerializer):
    challenger = serializers.SerializerMethodField(read_only=True)
    challenge_milestone = ChallengeMilestoneSerializer(read_only=True, many=True)

    @staticmethod
    def get_challenger(obj):
        return [challenger.id for challenger in obj.challenger.all()]

    class Meta:
        model = Challenge
        fields = "__all__"