from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
     path('blog/', views.blog, name='blog'),
     path('about/', views.about, name='about'),
     path('contact/', views.contact, name='contact'),
     path('faqs/', views.faqs, name='faqs'),
     path('search/', views.Blog_Search, name='Blog_Search'),
     path('save_contact/', views.save_contact, name='save_contact'),
     path('blog/<int:id>/<slug:slug>/', views.show_article, name='show_article'),
     path('add_comment/<int:id>/<slug:slug>/', views.save_comment, name='save_comment'),

     path('create_article/', views.create_article, name='create_article'),

     #privacy and terms
     path('Terms_and_conditions/', views.Terms_and_conditions, name='Terms_and_conditions'),
     path('privacy/', views.Privacy, name='Privacy'),


     #url
     #url(r'blog/(?P<id>\d+)/(?P<slug>[\w-]+)/$', views.show_article, name='show_article'),
    
     
]