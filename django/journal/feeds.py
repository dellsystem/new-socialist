from django.contrib.syndication.views import Feed

from journal.models import Article


class ArticleFeed(Feed):
    title = 'New Socialist'
    link = 'https://newsocialist.org.uk'
    description = 'Robust intellectual discussion and intransigent rabble rousing'

    def items(self):
        return Article.objects.filter(published=True).order_by('-date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.subtitle
