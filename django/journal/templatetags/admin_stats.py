import calendar
import datetime

from django import template
from django.urls import reverse
from django.utils.html import format_html

from journal.models import Article


register = template.Library()


MALE_LABEL = '<i class="inverted circular small black male icon" title="Male author(s)"></i>'
PUBLISHED_LABEL = '<i class="circular small checkmark icon" title="Published"></i>'
READY_LABEL = '<i class="circular small inverted green warning icon" title="Unpublished but ready"></i>'
NOT_READY_LABEL = '<i class="circular small inverted red x icon" title="Unpublished and not ready"></i>'
@register.simple_tag
def show_article_calendar():
    today = datetime.datetime.today()
    current_day = today.day

    num_non_days, num_days = calendar.monthrange(2018, 10)
    non_days_html = format_html('<div class="column"></div>' * num_non_days)
    days_html = []
    for i in range(num_days):
        day = i + 1
        articles = Article.objects.filter(
            date=datetime.date(today.year, today.month, day)
        )
        articles_html = []
        for article in articles:
            title = article.title
            if len(title) > 32:
                title = title[:30] + '...'
            # If the article is published, no status label needed.
            if article.published:
                status_label = PUBLISHED_LABEL
            else:
                if article.editor_notes:
                    status_label = NOT_READY_LABEL
                else:
                    status_label = READY_LABEL

            articles_html.append(
                '<a href="{url}" title="{full_title} by {authors}">{title}</a><br />{male_label}{status_label}'.format(
                    full_title=article.title,
                    authors=', '.join(a.name for a in article.authors.all()),
                    title=title,
                    url=reverse('editor:journal_article_change', args=[article.pk]),
                    male_label=MALE_LABEL if article.is_all_male() else '',
                    status_label=status_label,
                )
            )

        days_html.append(
            """
                <div class="{colour}column">
                    <h3 class="ui header">{day}</h3>
                    {articles}
                </div>
            """.format(
                colour='highlighted ' if current_day == day else '',
                day=day,
                articles=format_html(''.join(articles_html)),
            )
        )

    return format_html(
        """
        <h1>Article calendar - {current_month}</h1>
        <div class="ui celled seven column grid">
            {non_days}
            {days}
        </div>
        """,
        current_month=calendar.month_name[today.month],
        non_days=non_days_html,
        days=format_html(''.join(days_html)),
    )


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
    male_homepage_count = len([a for a in homepage_articles if a.is_all_male()])
    male_homepage_percent = int(male_homepage_count / 12 * 100)

    scheduled = Article.objects.filter(published=False)
    male_scheduled_count = len([a for a in scheduled if a.is_all_male()])
    male_scheduled_percent = int(male_scheduled_count / scheduled.count() * 100)

    return format_html(
        """
        <div class="ui four statistics">
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
                    scheduled
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
            <div class="statistic">
                <div class="value">
                    {}%
                </div>
                <div class="label">
                    male scheduled
                </div>
            </div>
        </div>
        """,
        last_30_days,
        scheduled.count(),
        male_homepage_percent,
        male_scheduled_percent,
    )
