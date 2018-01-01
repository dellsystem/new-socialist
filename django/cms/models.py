from django.db import models

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from martor.models import MartorField
from martor.utils import markdownify


class Page(models.Model):
    image = ProcessedImageField(
        upload_to='pages',
        processors=[ResizeToFill(1920, 1080)],
        format='JPEG',
        options={'quality': 100},
    )
    title = models.CharField(max_length=100, blank=True)
    subtitle = models.TextField(blank=True)
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    slug = models.SlugField(blank=True, unique=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.formatted_content = markdownify(self.content)
        super().save(*args, **kwargs)
