from django.contrib import admin


class EditorAdmin(admin.AdminSite):
    site_header = 'New Socialist — Editor'


editor_site = EditorAdmin(name='editor')
admin.site.site_header = 'New Socialist — SUDO'
