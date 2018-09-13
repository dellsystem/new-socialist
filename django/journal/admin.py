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


class IssueAdmin(CompareVersionAdmin):
    list_display = ['title', 'date']


class TagAdmin(CompareVersionAdmin):
    list_display = ['name', 'display_label', 'slug', 'list_editors', 'get_article_count']
    prepopulated_fields = {'slug': ('name',)}

    def get_article_count(self, obj):
        return obj.articles.count()
    get_article_count.short_description = 'Number of articles'

    def display_label(self, obj):
        return mark_safe(
            '<div class="ui {c} label">{t}</div>'.format(
                c=obj.colour,
                t=obj.short_name or obj.name
            )
        )

    def list_editors(self, obj):
        if obj.editors.count():
            return ', '.join(e.author.name for e in obj.editors.all())
        else:
            return '--'


class AuthorAdmin(CompareVersionAdmin):
    list_display = ['name', 'slug', 'is_male', 'get_article_count']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

    def get_article_count(self, obj):
        return obj.articles.count()
    get_article_count.short_description = 'Number of articles'


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
    list_display = ['display_title', 'date', 'show_image', 'list_authors',
        'list_tags', 'get_word_count','published']
    readonly_fields = ['image_thumbnail']
    list_filter = ['tags', 'published']
    search_fields = ['title', 'authors__name']
    prepopulated_fields = {'slug': ('title',)}
    change_form_template = 'admin/edit_article.html'
    actions = [make_published]
    form = ArticleForm
    list_display_links = None

    def changelist_view(self, request, extra_context=None):
        extra_context = {'title': 'Published and unpublished articles'}
        return super(ArticleAdmin, self).changelist_view(
            request, extra_context=extra_context
        )

    def display_title(self, obj):
        to_return = (
            '<h3 class="ui header"><a href="{u}">{t}</a><div class="sub header">{s}</div></h3>'.format(
                u=reverse('admin:journal_article_change', args=[obj.id]),
                t=obj.title,
                s=obj.subtitle or '<em>No subtitle</em>'
            )
        )
        if not obj.published:
            text = 'UNPUBLISHED - '

            if obj.editor_notes:
                text += obj.editor_notes
                colour = 'red'
                try:
                    if obj.commission.link:
                        text += ' (<a href="{}">Google docs</a>)'.format(
                            obj.commission.link
                        )
                except models.Commission.DoesNotExist:
                    pass
            else:
                colour = 'green'
                text += 'ready'
            to_return += '<span class="ui large {c} label">{t}</span>'.format(
                c=colour,
                t=text,
            )
        return mark_safe(to_return)
    display_title.admin_order_field = 'article__title'

    def list_tags(self, obj):
        return mark_safe(
            ''.join(
                '<span class="ui {c} label">{t}</span>'.format(
                    c=tag.colour,
                    t=tag.short_name or tag.name
                ) for tag in obj.tags.all())
        )
    list_tags.short_description = 'Tag(s)'

    def list_authors(self, obj):
        if obj.authors.count():
            to_return = ', '.join(
                format_html(
                    '<a href="{}">{}</a>',
                    reverse('admin:journal_author_change', args=[a.id]),
                    a.name
                )
                for a in obj.authors.all()
            )
        else:
            to_return = 'anonymous'
        if obj.is_all_male():
            to_return += '<br /><div class="ui black label">Male author(s)</div>'
        return mark_safe(to_return)
    list_authors.short_description = 'Author(s)'

    def get_word_count(self, obj):
        return obj.get_word_count()
    get_word_count.short_description = 'Words'

    def show_image(self, obj):
        to_return = '<img src="{}" class="ui medium image" />'.format(
            obj.get_image_thumbnail_url()
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


class CommissionAdmin(CompareVersionAdmin):
    list_display = ['get_details', 'display_editor', 'list_tags',
        'get_remind_after', 'get_scheduled_for', 'link_to_action'
    ]
    list_filter = ['editor', 'tags']
    list_display_links = None

    def changelist_view(self, request, extra_context=None):
        extra_context = {
            'title': 'Manage commissions (highlighted = needs action from us)'
        }
        self.user = request.user
        return super(CommissionAdmin, self).changelist_view(
            request, extra_context=extra_context
        )

    def display_editor(self, obj):
        if self.user == obj.editor.user:
            return mark_safe(
                '<div class="ui black button">You</div>'
            )
        else:
            return obj.editor
    display_editor.short_description = 'Lead editor'

    def get_details(self, obj):
        if obj.last_updated:
            updated = ' (last updated {})'.format(naturalday(obj.last_updated))
        else:
            updated = ''

        if obj.needs_action:
            segment_class = 'yellow inverted'
        else:
            segment_class = ''


        to_return = '<div class="ui basic compact {segment} segment"><h3 class="ui header"><a href="{url}">{writer} ~ {topic}</a><div class="sub header">{status}{updated}</div></h3></div>'.format(
            url=reverse('admin:journal_commission_change', args=[obj.id]),
            writer=obj.writer,
            topic=obj.topic,
            status=obj.status,
            segment=segment_class,
            updated=updated,
        )
        return mark_safe(to_return)
    get_details.short_description = 'Details'

    def link_to_action(self, obj):
        if obj.article:
            return mark_safe(
                '<a href="{}" class="ui black button">Article</a>'.format(
                    reverse('admin:journal_article_change', args=[obj.article.id])
                )
            )

        if obj.link:
            return mark_safe(
                '<a href="{}" class="ui button">Draft</a>'.format(obj.link)
            )

    link_to_action.short_description = 'Edit'

    def get_remind_after(self, obj):
        if obj.remind_after <= datetime.date.today():
            return mark_safe(
                '<strong>{}</strong>'.format(naturalday(obj.remind_after))
            )
        else:
            return naturalday(obj.remind_after)
    get_remind_after.short_description = 'Follow up after'

    def get_scheduled_for(self, obj):
        if obj.article:
            return mark_safe(
                '<strong>{}</strong>'.format(naturalday(obj.article.date))
            )
        else:
            return 'No article yet'
    get_scheduled_for.short_description = 'Scheduled for'
    get_scheduled_for.admin_order_field = 'article__date'

    def list_tags(self, obj):
        return mark_safe(
            ''.join(
                '<span class="ui {c} label">{t}</span>'.format(
                    c=tag.colour,
                    t=tag.short_name or tag.name
                ) for tag in obj.tags.all())
        )
    list_tags.short_description = 'Tag(s)'


class EditorAdmin(CompareVersionAdmin):
    list_display = ['author', 'user', 'section']
    list_filter = ['section']


editor_site.register(models.Issue, IssueAdmin)
editor_site.register(models.Article, ArticleAdmin)
editor_site.register(models.ArticleTranslation, ArticleTranslationAdmin)
editor_site.register(models.Author, AuthorAdmin)
editor_site.register(models.Tag, TagAdmin)
editor_site.register(models.Commission, CommissionAdmin)

admin.site.register(models.Issue, IssueAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleTranslation, ArticleTranslationAdmin)
admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Commission, CommissionAdmin)
admin.site.register(admin.models.LogEntry, LogEntryAdmin)
admin.site.register(models.Editor, EditorAdmin)
