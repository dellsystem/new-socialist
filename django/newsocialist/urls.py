"""newsocialist URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from newsocialist.admin import editor_site

import journal.views
import newsocialist.views
import cms.views
from journal.sitemaps import *
from cms.sitemaps import *

sitemaps = {
    'articles': ArticleSitemap(),
    'article_translations': ArticleTranslationSitemap(),
    'authors': AuthorSitemap(),
    'tags': TagSitemap(),
    'pages': PageSitemap(),
}


urlpatterns = [
    path('', newsocialist.views.index, name='index'),
    path('page/<int:number>/', newsocialist.views.archives, name='archives'),
    path('about/', newsocialist.views.about, name='about'),
    path('get-involved/', newsocialist.views.get_involved, name='get-involved'),
    path('the-new-socialist-collective/', newsocialist.views.editors, name='editors'),
    path('martor/', include('martor.urls')),
    path('sudo/', admin.site.urls),
    path('editor/', editor_site.urls),
    path('author/<slug:slug>', journal.views.AuthorView.as_view(), name='author'),
    path('tag/<slug:slug>/', journal.views.TagView.as_view(), name='tag'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('<slug:slug>/', newsocialist.views.article_or_page, name='article_or_page'),
    path('<slug:slug>/amp/', newsocialist.views.article_or_page, name='amp'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
