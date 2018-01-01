"""notesfrombelow URL Configuration

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

from notesfrombelow.admin import editor_site

import journal.views
import notesfrombelow.views


urlpatterns = [
    path('', notesfrombelow.views.index, name='index'),
    path('about', notesfrombelow.views.about, name='about'),
    path('contribute', notesfrombelow.views.contribute, name='contribute'),
    path('martor/', include('martor.urls')),
    path('sudo/', admin.site.urls),
    path('editor/', editor_site.urls),
    path('author/<slug:slug>', journal.views.AuthorView.as_view(), name='author'),
    path('category/<slug:slug>', journal.views.CategoryView.as_view(), name='category'),
    path('<slug:slug>', journal.views.ArticleView.as_view(), name='article'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
