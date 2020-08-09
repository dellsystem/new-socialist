from django.shortcuts import render
from django.views import generic

from .models import Article, Tag, Author, Edition


class TagView(generic.DetailView):
    model = Tag
    template_name = 'tag.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = Tag.objects.exclude(editors=None).order_by('name')
        return context


class AuthorView(generic.DetailView):
    model = Author
    template_name = 'author.html'


class EditionListView(generic.ListView):
    model = Edition
    template_name = 'view_editions.html'


class EditionView(generic.DetailView):
    model = Edition
    template_name = 'view_edition.html'
