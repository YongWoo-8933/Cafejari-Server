from cafe.models import DailyActivityStack


def clear_activity_stack():
    DailyActivityStack.objects.all().delete()