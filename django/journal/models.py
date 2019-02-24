import operator
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags

from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
from martor.models import MartorField
from martor.utils import markdownify


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = MartorField(blank=True)
    formatted_bio = models.TextField(editable=False)
    twitter = models.CharField(max_length=15, blank=True, null=True,
        help_text='Username (without the @)')
    slug = models.SlugField(
        unique=True,
        help_text="Please do not change this after the author is live."
    )
    is_male = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_articles(self):
        return self.articles.filter(published=True)

    def get_absolute_url(self):
        return reverse('author', args=[self.slug])

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_bio = markdownify(self.bio)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(
        max_length=20,
        blank=True,
        help_text='For internal use only'
    )
    colour = models.CharField(
        max_length=20,
        blank=True,
        help_text='For internal use only'
    )
    slug = models.SlugField(unique=True, max_length=50)
    description = models.TextField()
    content = MartorField(blank=True)
    formatted_content = models.TextField(editable=False)
    email = models.EmailField(blank=True)
    image_credit = models.TextField(blank=True)
    formatted_image_credit = models.TextField(editable=False)
    image = ProcessedImageField(
        upload_to='tags',
        processors=[ResizeToFill(1115, 450)],
        options={'quality': 100},
        blank=True
    )

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return '/static/img/banner.png'

    def get_articles(self):
        return self.articles.filter(published=True)

    def get_absolute_url(self):
        return reverse('tag', args=[self.slug])

    def save(self, *args, **kwargs):
        # Parse markdown and cache it.
        self.formatted_image_credit = markdownify(self.image_credit)
        self.formatted_content = markdownify(self.content)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Editor(models.Model):
    author = models.OneToOneField(
        Author, on_delete=models.CASCADE, primary_key=True
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    section = models.ForeignKey(
        Tag, on_delete=models.CASCADE, blank=True, null=True,
        help_text='Leave blank if not a section editor',
        related_name='editors',
    )
    wants_emails = models.BooleanField(default=False)
    is_online_editor = models.BooleanField(
        default=False,
        help_text='Will have the ability to approve articles + gets email reminders'
    )

    def __str__(self):
        return self.author.name


    def get_overdue_commissions(self):
        return self.commissions.filter(remind_after__lte=datetime.date.today())



class Issue(models.Model):
    title = models.CharField(max_length=50)
    date = models.DateField(help_text='Day ignored')
    image = ProcessedImageField(
        upload_to='issues',
        processors=[ResizeToFill(1920, 450)],
        options={'quality': 100},
        blank=True
    )

    def __str__(self):
        return self.title


class Article(models.Model):
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=100, unique=True)
    authors = models.ManyToManyField(Author, related_name='articles',
        blank=True)
    subtitle = models.CharField(max_length=215, blank=True)
    content = MartorField(blank=True)
    formatted_content = models.TextField(editable=False)
    # Store the formatted_content field with all tags removed (for related)
    unformatted_content = models.TextField(editable=False)
    date = models.DateField()
    issue = models.ForeignKey(Issue, related_name='articles', null=True,
        blank=True, on_delete=models.CASCADE)
    editor_notes = models.CharField(max_length=255, blank=True)
    image = ProcessedImageField(
        upload_to='articles',
        processors=[ResizeToFill(1115, 450)],
        format='JPEG',
        options={'quality': 100},
        blank=True
    )
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(540, 350)],
        format='JPEG',
        options={'quality': 90}
    )
    custom_thumbnail = ProcessedImageField(
        upload_to='thumbnails',
        processors=[ResizeToFill(540, 350)],
        format='JPEG',
        options={'quality': 100},
        blank=True
    )
    background_position = models.CharField(max_length=50, blank=True)
    image_credit = models.TextField(blank=True)
    formatted_image_credit = models.TextField(editable=False)
    related_1 = models.ForeignKey("self", related_name='related_1_articles',
        on_delete=models.CASCADE, limit_choices_to={'published': True}, blank=True,
        null=True)
    related_2 = models.ForeignKey("self", related_name='related_2_articles',
        on_delete=models.CASCADE, limit_choices_to={'published': True}, blank=True,
        null=True)
    last_modified = models.DateField(auto_now=True)
    verified = models.BooleanField(default=False)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return self.title

    def get_days_overdue(self):
        if not self.published:
            today = datetime.date.today()
            days = (today - self.date).days
            if days > 0:
                return days

    def is_all_male(self):
        # Only if the article is not anonymous, and has no non-male authors.
        return (
            self.authors.exists() and
            not self.authors.filter(is_male=False).exists()
        )

    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return '/static/img/banner.png'

    def get_image_thumbnail_url(self):
        if self.custom_thumbnail:
            return self.custom_thumbnail.url
        elif self.image_thumbnail:
            return self.image_thumbnail.url
        else:
            return '/static/img/placeholder.png'

    def get_full_url(self):
        return settings.SITE_URL + self.get_absolute_url()

    def get_absolute_url(self):
        return reverse('article-or-page', args=[self.slug])

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
        self.formatted_image_credit = markdownify(self.image_credit)
        self.formatted_content = markdownify(self.content)
        self.unformatted_content = strip_tags(self.formatted_content)

        # Must save before attempting to access a ManyToManyField (tags)
        super().save(*args, **kwargs)

        # Only set the related articles if they haven't already been specified.
        if not self.related_1 or not self.related_2:
            # Check if the smallest tag has at least two other articles.
            tags = []
            for tag in self.tags.all():
                articles = tag.articles.exclude(pk=self.pk).exclude(published=False)
                if articles.count() >= 2:
                    tags.append((articles, articles.count()))
            tags.sort(key=operator.itemgetter(1))
            if tags:
                # Find two articles in this tag that are older, or just the oldest.
                articles  = tags[0][0]
                older_articles = articles.order_by('-date').exclude(date__gt=self.date)
                if older_articles.count() < 2:
                    related_articles = articles.order_by('date')
                else:
                    related_articles = older_articles
            else:
                related_articles = Article.objects.exclude(pk=self.pk).exclude(
                    published=False
                )

            if not self.related_1:
                self.related_1 = related_articles[0]
            if not self.related_2:
                self.related_2 = related_articles[1]

        super().save(*args, **kwargs)

    # Use h2 or h3 in article thumbnail depending on the length of the title.
    def get_title_header(self):
        if len(self.title) > 50:
            return 'h4'
        else:
            return 'h3'

    def get_related(self):
        # Limited to 2. Currently just gets the latest articles.
        related = []
        if self.related_1:
            related.append(self.related_1)
        if self.related_2:
            related.append(self.related_2)
        return related


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
        return reverse('article', args=[self.article.slug]) + '?language=' + self.language


class ArticleDetails(models.Model):
    """For managing the social media sharing details."""
    article = models.OneToOneField(
        Article,
        on_delete=models.CASCADE,
        related_name='details',
    )
    twitter_text = models.TextField(
        null=True,
        blank=True,
        help_text="Draft tweet text here."
    )
    facebook_text = models.TextField(
        null=True,
        blank=True,
        help_text="Draft Facebook post text here."
    )
    screenshot_1 = models.ImageField(null=True, blank=True)
    screenshot_2 = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.article.title


class Commission(models.Model):
    article = models.OneToOneField(Article,
        on_delete=models.CASCADE,
        related_name='commission',
        blank=True,
        null=True,
    )
    editor = models.ForeignKey(Editor,
        related_name='commissions',
        on_delete=models.CASCADE
    )
    topic = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, related_name='commissions')
    writer = models.CharField(max_length=255)
    status = models.TextField()
    last_updated = models.DateField(auto_now=True)
    needs_action = models.BooleanField(
        default=False,
        help_text='whether it needs action from us (otherwise - waiting for author)'
    )
    remind_after = models.DateField(
        help_text='Check in on (or respond to) the author after this date.'
    )
    link = models.URLField(blank=True, help_text='Link to Google doc')

    class Meta:
        ordering =  ['remind_after']

    def __str__(self):
        return self.topic

    def get_days_overdue(self):
        today = datetime.date.today()
        days = (today - self.remind_after).days
        if days > 0:
            return days
