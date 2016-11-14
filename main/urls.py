from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^new-subject/$', views.new_subject, name='new-subject'),
    url(r'^create-cards/$', views.create_cards, name='create-cards'),
    url(r'^delete-subject/$', views.delete_subject, name="delete-subject"),
    url(r'^register/$', views.register, name="register"),
    url(r'^login/$', views.user_login, name="login"),
    url(r'^logout/$', views.user_logout, name="logout"),
    url(r'^rest/cards/$', views.rest_card, name="rest-card"),
]
