from rest_framework import serializers

from challenge.serializers import ChallengeMilestoneSerializer
from utils import SwaggerSerializer

# request serializer
class SwaggerChallengeParticipateRequestSerializer(SwaggerSerializer):
    challenge_id = serializers.IntegerField()

# response serializer
class SwaggerChallengeResponseSerializer(SwaggerSerializer):
    name = serializers.CharField(max_length=63)
    description = serializers.CharField()
    image = serializers.URLField()
    available = serializers.BooleanField(default=True)
    start = serializers.DateTimeField()
    finish = serializers.DateTimeField()
    participant_limit = serializers.IntegerField()
    goal = serializers.IntegerField()
    challenger = serializers.ListField(child=serializers.IntegerField())
    challenge_milestone = ChallengeMilestoneSerializer(many=True)


