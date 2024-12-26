from .views import * 
from django.urls import path 

urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('search/', PostList.as_view(), name='post_detail'),
    path('<int:pk>/', PostDetail.as_view(), name='post_filter'),
    path('news/create/', PostCreate.as_view(), name='news_create'),
    path('article/create/', PostCreate.as_view(), name='article_create'),
    path('<int:pk>/post_edit/', PostUpdate.as_view(), name='news_edit'),
    path('article/<int:pk>/post_edit/', PostUpdate.as_view(), name='article_edit'),
    path('<int:pk>/post_delete/', PostDelete.as_view(), name='news_delete'),
    path('article/<int:pk>/post_delete/', PostDelete.as_view(), name='article_delete'),
    path('categories/<int:pk>/subscribe/', subscribe_category, name='subscribe_category'),
    path('', IndexView.as_view()),
]