from django.db import models
from sellers.models import Shop
from django.utils import timezone



class Story(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/story_files',null=True,blank=True)  # فقط یک فیلد آپلود
    video = models.FileField(upload_to='media/story_video', null=True, blank=True)
    image = models.ImageField(upload_to='media/story_image', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.file:
            content_type = self.file.file.content_type  # نوع فایل (mime)
            if content_type.startswith('image'):
                self.image = self.file
                self.video = None

            elif content_type.startswith('video'):
                self.video = self.file
                self.image = None
        super().save(*args, **kwargs)

    def is_expired(self):
        if self.expiry_time:
            return timezone.now() > self.expiry_time
        return None

    def __str__(self):
        return f"Story from {self.shop} at {self.created_at}"