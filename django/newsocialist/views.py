import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from journal.forms import ArticleDetailsForm
from journal.models import Article, ArticleDetails, Author, Tag
from cms.models import Page


def archives(request, number):
    all_articles = Article.objects.filter(published=True).order_by('-date')
    paginator = Paginator(all_articles, 6)
    articles = paginator.get_page(number)
    sections = Tag.objects.exclude(editors=None).order_by('name')

    context = {
        'articles': articles,
        'page_number': number,
        'total_pages': paginator.num_pages,
        'sections': sections,
    }

    return render(request, 'archives.html', context)


def index(request):
    page = Page.objects.get(slug='')

    articles = Article.objects.filter(published=True).order_by('-date').distinct()[:12]

    today = datetime.date.today()
    unpublished = Article.objects.filter(published=False, date__lte=today)

    context = {
        'unpublished': unpublished,
        'articles': articles,
        'page': page,
    }

    return render(request, 'index.html', context)


@staff_member_required
def share_article(request, slug):
    try:
        article = Article.objects.filter(slug=slug).first()
    except Article.DoesNotExist:
        raise Http404

    article_details, created = ArticleDetails.objects.get_or_create(
        article=article,
    )

    context = {
        'article': article,
        'article_details': article_details,
    }

    return render(request, 'share_article.html', context)


@staff_member_required
def manage_article(request, slug):
    try:
        article = Article.objects.filter(slug=slug).first()
    except Article.DoesNotExist:
        raise Http404

    article_details, created = ArticleDetails.objects.get_or_create(
        article=article,
    )

    if request.method == 'POST':
        form = ArticleDetailsForm(request.POST, request.FILES, instance=article_details)
        if form.is_valid():
            form.save()
    else:
        article_url = article.get_full_url()
        initial = {}
        if article_details.twitter_text is None:
            initial['twitter_text'] = '{authors} {url}'.format(
                authors=' ,'.join('@' + a.twitter if a.twitter else a.name for a in article.authors.all()),
                url=article_url
            )
        if article_details.facebook_text is None:
            initial['facebook_text'] = '{authors} {url}'.format(
                authors=' ,'.join(a.name for a in article.authors.all()),
                url=article_url
            )
        form = ArticleDetailsForm(instance=article_details, initial=initial)

    context = {
        'article': article,
        'form': form,
    }

    return render(request, 'manage_article.html', context)


@staff_member_required
@require_POST
def publish_article(request, slug):
    try:
        article = Article.objects.filter(slug=slug).first()
    except Article.DoesNotExist:
        raise Http404

    if not article.published:
        article.published = True
        article.save()

    return redirect('share-article', slug=article.slug)


@staff_member_required
def unpublish_article(request, slug):
    try:
        article = Article.objects.filter(slug=slug).first()
    except Article.DoesNotExist:
        raise Http404

    if request.POST:
        article.published = False
        article.save()
        return redirect(article)

    context = {
        'article': article,
    }

    return render(request, 'unpublish_article.html', context)


def article_or_page(request, slug):
    article = Article.objects.filter(slug=slug).first()
    if article is not None:
        desired_language_code = request.GET.get('language')
        desired_language_name = None  # not needed for English
        all_languages = []
        desired_translation = None

        for translation in article.translations.all():
            language_name = translation.get_language_display()
            all_languages.append((translation.language, language_name))
            if translation.language == desired_language_code:
                desired_language_name = language_name
                desired_translation = translation

        # If the get parameter doesn't match an existing translation, use en.
        if desired_translation is None:
            desired_language_code = 'en'
            desired_translation = article

        # Only add these context variables if translations exist.
        if all_languages:
            all_languages.append(('en', 'English'))

        context = {
            'article': article,
            'formatted': desired_translation.formatted_content,
            'unformatted': desired_translation.unformatted_content,
            'title': desired_translation.title,
            'desired_language_code': desired_language_code,
            'desired_language_name': desired_language_name,
            'languages': all_languages,
        }

        return render(request, 'article.html', context)

    page = Page.objects.filter(slug=slug).first()
    if page is not None:
        return render(request, 'page.html', {'page': page})

    # See if there's a tag with this slug.
    tag = Tag.objects.filter(slug=slug).first()
    if tag is not None:
        return redirect(tag)

    raise Http404


def editors(request):
    page = Page.objects.get(slug='the-new-socialist-collective')
    sections = Tag.objects.filter(editors__isnull=False).distinct()
    general_editors = [
        ('General Editor', Author.objects.get(slug='tom')),
        ("Readers' Editor", Author.objects.get(slug='jude')),
        ("Contributing Editor", Author.objects.get(slug='daniel')),
    ]
    other_contributors = [
        ('Design', Author.objects.get(slug='tom-munday')),
        ('Web', Author.objects.get(slug='joe-corcoran')),
    ]

    context = {
        'page': page,
        'sections': sections,
        'general_editors': general_editors,
        'other_contributors': other_contributors,
    }

    return render(request, 'editors.html', context)


def about(request):
    page = Page.objects.get(slug='about')
    contributors = Author.objects.filter(
        articles__published=True
    ).order_by('name').distinct()

    context = {
        'page': page,
        'contributors': contributors,
    }

    return render(request, 'about.html', context)


def get_involved(request):
    page = Page.objects.get(slug='get-involved')

    context = {
        'page': page,
    }

    return render(request, 'get_involved.html', context)


def search(request):
    query = request.GET.get('q', '')

    if not query:
        return redirect('archives', number=1)

    if len(query) < 3:
        articles = None
        authors = None
    else:
        articles = Article.objects.filter(
            Q(title__icontains=query) | Q(subtitle__icontains=query)
        ).exclude(published=False)
        authors = Author.objects.filter(
            Q(name__icontains=query) | Q(twitter__icontains=query)
        )

    context = {
        'authors': authors,
        'articles': articles,
        'query': query,
    }

    return render(request, 'search.html', context)
