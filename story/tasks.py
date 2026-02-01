from datetime import timedelta
from django.utils import timezone
from story.models import Story
from celery import shared_task

@shared_task
def default_disactive_history():
    expiry_time = timezone.now() - timedelta(hours=24)
    old_stories = Story.objects.filter(created_at__lt=expiry_time, active=True)
    old_stories.update(active=False)
    old_stories.delete()


# def defult_remove_storys_after_3_month():
#     three_months_ago = timezone.now() - timedelta(days=90)
#     Story.objects.filter(created_at__lt=three_months_ago).delete()