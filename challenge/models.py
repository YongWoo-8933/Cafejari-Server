
from django.db import models


def challenge_image_upload_path(instance, filename):
        return f"challenge/{instance.start.year}/{instance.start.month}/{instance.name}/{filename}"

class Challenge(models.Model):
    name = models.CharField(max_length=63)
    description = models.TextField()
    image = models.ImageField(upload_to=challenge_image_upload_path)
    available = models.BooleanField(default=True)
    start = models.DateTimeField()
    finish = models.DateTimeField()
    participant_limit = models.IntegerField(null=True, blank=True, default=None)
    goal = models.IntegerField()

    class Meta:
        db_table = 'challenge_challenge'
        db_table_comment = '기본 챌린지 모델'
        app_label = 'challenge'
        ordering = ['-start']


class ChallengeMilestone(models.Model):
    progress_rate = models.DecimalField(max_digits=3, decimal_places=2)
    description = models.TextField(max_length=63)
    point = models.IntegerField()
    count = models.IntegerField()
    challenge = models.ForeignKey(
        'Challenge',
        on_delete=models.CASCADE,
        related_name="challenge_milestone",
        db_column="challenge"
    )

    class Meta:
        db_table = 'challenge_challenge_milestone'
        db_table_comment = '챌린지의 포인트 정산 지점 모델'
        app_label = 'challenge'
        ordering = ['-challenge']


class Challenger(models.Model):
    progress_rate = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    count = models.IntegerField(default=0)
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name="challenger",
        db_column="user"
    )
    challenge = models.ForeignKey(
        'Challenge',
        on_delete=models.CASCADE,
        related_name="challenger",
        db_column="challenge"
    )

    class Meta:
        db_table = 'challenge_challenger'
        db_table_comment = '챌린지 도전자 모델'
        app_label = 'challenge'
        ordering = ['-challenge']


class ChallengePoint(models.Model):
    rewarded_at = models.DateTimeField(auto_now_add=True)
    point = models.IntegerField()
    description = models.TextField()
    challenger = models.ForeignKey(
        'Challenger',
        on_delete=models.CASCADE,
        related_name="challenge_point",
        db_column="challenger"
    )

    class Meta:
        db_table = 'challenge_point'
        db_table_comment = '챌린지 보상 포인트 모델'
        app_label = 'challenge'
        ordering = ['-rewarded_at']