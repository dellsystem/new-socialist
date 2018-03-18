from django.contrib.sitemaps import Sitemap

from journal.models import *


class ArticleSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.7

    def items(self):
        return Article.objects.filter(published=True)

    def lastmod(self, item):
        return item.last_modified


class ArticleTranslationSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.7

    def items(self):
        return ArticleTranslation.objects.filter(article__published=True).order_by('pk')

    def lastmod(self, item):
        return item.last_modified


class AuthorSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.4

    def items(self):
        return Author.objects.filter(articles__published=True).order_by('name').distinct()

    def lastmod(self, item):
        try:
            return item.articles.latest().date
        except Article.DoesNotExist:
            return None


class TagSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Tag.objects.order_by('name')

    def lastmod(self, item):
        try:
            return item.articles.latest().date
        except Article.DoesNotExist:
            return None
