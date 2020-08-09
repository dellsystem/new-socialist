from django.shortcuts import render
from django.views import generic

from transmissions.models import Article



class ListView(generic.ListView):
    model = Article
    paginate_by = 100
    template_name = 'view_transmissions.html'


def view_transmission(request, slug):
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

        return render(request, 'view_transmission.html', context)

