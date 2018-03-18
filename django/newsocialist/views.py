from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render

from journal.models import Article, Author, Tag
from cms.models import Page


def archives(request, number):
    all_articles = Article.objects.filter(published=True).order_by('-date')
    paginator = Paginator(all_articles, 6)
    articles = paginator.get_page(number)

    context = {
        'articles': articles,
        'page_number': number,
        'total_pages': paginator.num_pages,
    }

    return render(request, 'archives.html', context)


def index(request):
    articles = Article.objects.filter(published=True, featured=False).order_by('-date')[:5]
    page = Page.objects.get(slug='')

    all_articles = Article.objects.filter(published=True).order_by('-date')

    featured = all_articles.filter(featured=True)[:2]
    non_featured = all_articles.exclude(
        pk__in=featured.values_list('pk', flat=True)
    )

    context = {
        'non_featured': non_featured,
        'featured': featured,
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
    section_editors = Author.objects.filter(is_editor=True)
    sections = Tag.objects.filter(editors__isnull=False).distinct()
    general_editors = [
        ('General Editor', Author.objects.get(slug='tom-gann')),
        ("Readers' Editor", Author.objects.get(slug='jude-wanga')),
        ("Contributing Editor", Author.objects.get(slug='dan-frost')),
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
