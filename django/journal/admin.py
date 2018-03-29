from django import forms
from django.db.models import Count
from django.contrib import admin

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


class ArticleAdmin(CompareVersionAdmin):
    list_display = ['title', 'list_authors', 'list_tags', 'date',
        'get_word_count','published', 'featured']
    readonly_fields = ['image_thumbnail']
    list_filter = ['issue', 'tags',]
    search_fields = ['title', 'authors__name']
    prepopulated_fields = {'slug': ('title',)}
    change_form_template = 'admin/edit_article.html'
    form = ArticleForm

    def list_tags(self, obj):
        return ', '.join(t.name for t in obj.tags.all())

    def list_authors(self, obj):
        if obj.authors.count():
            return ', '.join(a.name for a in obj.authors.all())
        else:
            return 'anonymous'


class ArticleTranslationAdmin(CompareVersionAdmin):
    list_display = ['article', 'title', 'language']


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
