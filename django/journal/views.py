from django.shortcuts import render
from django.views import generic

from .models import Article, Tag, Author, Issue


class TagView(generic.DetailView):
    model = Tag
    template_name = 'tag.html'


class AuthorView(generic.DetailView):
    model = Author
    template_name = 'author.html'


class IssueView(generic.DetailView):
    model = Issue
    template_name = 'issue.html'
