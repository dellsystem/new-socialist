from django import forms
from django.db.models import Count
from django.contrib import admin
from django.utils.html import mark_safe

from reversion_compare.admin import CompareVersionAdmin

from newsocialist.admin import editor_site
from . import models


class IssueAdmin(CompareVersionAdmin):
    list_display = ['title', 'date']


class TagAdmin(CompareVersionAdmin):
    list_display = ['name', 'slug', 'get_article_count', 'list_editors']
    prepopulated_fields = {'slug': ('name',)}

    def get_article_count(self, obj):
        return obj.articles.count()

    def list_editors(self, obj):
        if obj.editors.count():
            return ', '.join(e.name for e in obj.editors.all())
        else:
            return '--'


class AuthorAdmin(CompareVersionAdmin):
    list_display = ['name', 'slug', 'get_article_count']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    list_filter = ['is_editor']

    def get_article_count(self, obj):
        return obj.articles.count()


class ArticleForm(forms.ModelForm):
    class Meta:
        model = models.Article
        fields = '__all__'
        widgets = {
            'image_credit': forms.Textarea(attrs={'rows': 2}),
            'tags': forms.SelectMultiple(
                attrs={
                    'class': 'ui search fluid dropdown multi-select',
                },
            ),
            'authors': forms.SelectMultiple(
                attrs={
                    'class': 'ui search fluid dropdown multi-select',
                },
            ),
            'subtitle': forms.Textarea(attrs={'rows': 2}),
            'related_2': forms.Select(
                attrs={
                    'class': 'ui search fluid dropdown',
                },
            ),
            'related_1': forms.Select(
                attrs={
                    'class': 'ui search fluid dropdown',
                },
            ),
        }


def make_published(modeladmin, request, queryset):
    queryset.update(published=True)
make_published.short_description = 'Mark selected articles as published'


class ArticleAdmin(CompareVersionAdmin):
    list_display = ['title', 'show_image', 'list_authors', 'list_tags', 'date',
        'get_word_count','published', 'featured']
    readonly_fields = ['image_thumbnail']
    list_filter = ['tags', 'published']
    search_fields = ['title', 'authors__name']
    prepopulated_fields = {'slug': ('title',)}
    change_form_template = 'admin/edit_article.html'
    actions = [make_published]
    form = ArticleForm

    def list_tags(self, obj):
        return ', '.join(t.name for t in obj.tags.all())
    list_tags.short_description = 'Tag(s)'

    def list_authors(self, obj):
        if obj.authors.count():
            return ', '.join(a.name for a in obj.authors.all())
        else:
            return 'anonymous'
    list_authors.short_description = 'Author(s)'

    def get_word_count(self, obj):
        return obj.get_word_count()
    get_word_count.short_description = 'Words'

    def show_image(self, obj):
        to_return = '<img src="{}" class="ui small image" />'.format(
            obj.image_thumbnail.url
        )
        return mark_safe(to_return)
    show_image.short_description = 'Image'


class ArticleTranslationAdmin(CompareVersionAdmin):
    list_display = ['article', 'title', 'language']


class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        '__str__', 'user', 'action_time', 'content_type', 'object_id'
    ]
    list_filter = ('user',)


editor_site.register(models.Issue, IssueAdmin)
editor_site.register(models.Article, ArticleAdmin)
editor_site.register(models.ArticleTranslation, ArticleTranslationAdmin)
editor_site.register(models.Author, AuthorAdmin)
editor_site.register(models.Tag, TagAdmin)

admin.site.register(models.Issue, IssueAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleTranslation, ArticleTranslationAdmin)
admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(admin.models.LogEntry, LogEntryAdmin)
