from rest_framework import serializers

from challenge.serializers import ChallengeResponseSerializer
from utils import SwaggerSerializer

# request serializer
class SwaggerChallengeParticipateRequestSerializer(SwaggerSerializer):
    challenge_id = serializers.IntegerField()

# response serializer
class SwaggerChallengeResponseSerializer(ChallengeResponseSerializer):
    challenger = serializers.ListField(child=serializers.IntegerField())


