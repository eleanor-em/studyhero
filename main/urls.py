from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new-subject/$', views.new_subject, name='new-subject'),
    url(r'^create-cards/$', views.create_cards, name='create-cards'),
]
