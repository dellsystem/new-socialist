from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
from martor.utils import markdownify
from django.urls import reverse

from journal.models import Author
from martor.models import MartorField


class Article(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=100, unique=True)
    authors = models.ManyToManyField(Author, related_name='transmissions',
        blank=True)
    subtitle = models.CharField(max_length=215, blank=True)
    content = MartorField(blank=True)
    formatted_content = models.TextField(editable=False)
    # Store the formatted_content field with all tags removed (for related)
    unformatted_content = models.TextField(editable=False)
    date = models.DateField()
    last_modified = models.DateField(auto_now=True)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return self.title

    def get_full_url(self):
        return settings.SITE_URL + self.get_absolute_url()

    def get_absolute_url(self):
        return reverse('view-transmission', args=[self.slug])

    def get_description(self):
        if self.authors.count():
            authors = ', '.join(a.name for a in self.authors.all())
        else:
            authors = 'anonymous'

        return 'by {authors} // {subtitle}'.format(
            authors=authors,
            subtitle=self.subtitle
        )

    def get_word_count(self):
        return len(self.unformatted_content.split())

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_content = markdownify(self.content)
        self.unformatted_content = strip_tags(self.formatted_content)

        # Must save before attempting to access a ManyToManyField (tags)
        super().save(*args, **kwargs)


class ArticleTranslation(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
        related_name='translations')
    language = models.CharField(max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(max_length=255)
    content = MartorField()
    formatted_content = models.TextField(editable=False)
    # Store the formatted_content field with all tags removed (for description)
    unformatted_content = models.TextField(editable=False)
    last_modified = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('article', 'language')

    def __str__(self):
        return "{}—{}".format(self.article.title, self.get_language_display())

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_content = markdownify(self.content)
        self.unformatted_content = strip_tags(self.formatted_content)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('view_transmission', args=[self.article.slug]) + '?language=' + self.language
