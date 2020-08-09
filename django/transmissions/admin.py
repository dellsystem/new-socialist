import datetime

from django import forms
from django.db.models import Count
from django.contrib import admin
from django.contrib.humanize.templatetags.humanize import naturalday
from django.urls import reverse
from django.utils.html import mark_safe, format_html

from reversion_compare.admin import CompareVersionAdmin

from newsocialist.admin import editor_site
from . import models


class ArticleAdmin(CompareVersionAdmin):
    list_display = ['title', 'date']


class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = '__all__'
        widgets = {
            'authors': forms.SelectMultiple(
                attrs={
                    'class': 'ui search fluid dropdown multi-select',
                },
            ),
            'subtitle': forms.Textarea(attrs={'rows': 2}),
        }


def make_published(modeladmin, request, queryset):
    queryset.update(published=True)
make_published.short_description = 'Mark selected articles as published'


class ArticleAdmin(CompareVersionAdmin):
    list_display = ['display_title', 'date', 'list_authors',
        'get_word_count','published']
    list_filter = ['published']
    search_fields = ['title', 'authors__name']
    prepopulated_fields = {'slug': ('title',)}
    change_form_template = 'admin/edit_transmission.html'
    actions = [make_published]
    form = ArticleForm
    list_display_links = None
    ordering = ['published', '-date']

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Published and unpublished articles'}
        return super(ArticleAdmin, self).changelist_view(
            request, extra_context=extra_context
        )

    def display_title(self, obj):
        to_return = (
            '<h3 class="ui header"><a href="{u}">{t}</a><div class="sub header">{s}</div></h3>'.format(
                u=reverse('editor:transmissions_article_change', args=[obj.id]),
                t=obj.title,
                s=obj.subtitle or '<em>No subtitle</em>'
            )
        )
        return mark_safe(to_return)
    display_title.admin_order_field = 'article__title'

    def list_authors(self, obj):
        if obj.authors.count():
            to_return = ', '.join(
                format_html(
                    '<a href="{}">{}</a>',
                    reverse('editor:journal_author_change', args=[a.id]),
                    a.name
                )
                for a in obj.authors.all()
            )
        else:
            to_return = 'anonymous'
        return mark_safe(to_return)
    list_authors.short_description = 'Author(s)'

    def get_word_count(self, obj):
        return obj.get_word_count()
    get_word_count.short_description = 'Words'


class ArticleTranslationAdmin(CompareVersionAdmin):
    list_display = ['article', 'title', 'language']


editor_site.register(models.Article, ArticleAdmin)
editor_site.register(models.ArticleTranslation, ArticleTranslationAdmin)

admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleTranslation, ArticleTranslationAdmin)
