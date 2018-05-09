from django.contrib import admin


class EditorAdmin(admin.AdminSite):
    site_header = 'New Socialist — Editor'
    index_template = 'admin_index.html'
    index_title = ''


editor_site = EditorAdmin(name='editor')
admin.site.site_header = 'New Socialist — SUDO'
