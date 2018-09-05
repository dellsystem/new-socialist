from django.db import models

from imagekit.processors import ResizeToFit
from imagekit.models import ProcessedImageField


class ImageUpload(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(
        help_text='For including the image in the article body. If the slug is "image-1", include it with [img:image-1]'
    )
    file = ProcessedImageField(
        upload_to='images',
        processors=[ResizeToFit(width=1115, upscale=False)],
    )

    def __str__(self):
        return self.title


class PdfUpload(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    file = models.FileField(upload_to='pdfs')

    def __str__(self):
        return self.title
