from django.conf.urls import url

from . import views

app_name = 'search'

urlpatterns = [

    url(r'^searchtarget/', views.searchtarget, name='searchtarget'),
    url(r'^([A-Za-z0-9 ]+)/$', views.search, name='search'),
]