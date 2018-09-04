from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render

from journal.models import Article, Author, Tag
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

    context = {
        'articles': articles,
        'page': page,
    }

    return render(request, 'index.html', context)


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
