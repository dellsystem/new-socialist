import datetime

from django import template
from django.utils.html import format_html

from journal.models import Article


register = template.Library()


@register.simple_tag
def show_article_stats():
    today = datetime.date.today()
    date_cutoff = today - datetime.timedelta(days=30)
    last_30_days = Article.objects.filter(
        published=True, date__gte=date_cutoff
    ).count()

    homepage_articles = Article.objects.filter(
        published=True
    ).order_by('-date').distinct()[:12]
    male_count = len([a for a in homepage_articles if a.is_all_male()])
    male_percent = int(male_count / 12 * 100)

    scheduled = Article.objects.filter(published=False).order_by('date')

    return format_html(
        """
        <div class="ui three statistics">
            <div class="statistic">
                <div class="value">
                    {}
                </div>
                <div class="label">
                    in the last 30 days
                </div>
            </div>
            <div class="statistic">
                <div class="value">
                    {}
                </div>
                <div class="label">
                    scheduled (until {})
                </div>
            </div>
            <div class="statistic">
                <div class="value">
                    {}%
                </div>
                <div class="label">
                    male on homepage
                </div>
            </div>
        </div>
        """,
        last_30_days,
        scheduled.count(),
        scheduled.last().date.strftime('%b %d'),
        male_percent,
    )
