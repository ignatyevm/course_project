from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('suggested-posts/', views.view_suggested_posts, name='suggested-post'),
    path('my-posts/', views.view_my_posts, name='my-posts'),
    path('post/<pk>/publish/', views.view_publish_post, name='post-publish'),
    path('post/<pk>/', views.post_detail, name='post-detail'),
    #path('new/', views.PostCreateView.as_view(), name='post-create'),
    path('new/', views.post_create, name='post-create'),
    path('post/<pk>/update', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<pk>/delete', views.PostDeleteView.as_view(), name='post-delete'),
]
