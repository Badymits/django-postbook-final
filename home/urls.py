from django.urls import path

from . import views

urlpatterns = [
    path('', views.homePage, name='home'),
    path('create-post/', views.createPost, name='create-post'),
    path('detail-post/<int:id>/', views.detailPost, name='detail-post'),
    path('edit-post/<int:id>/', views.editPost, name='edit-post'),
    path('delete-post/<int:id>/', views.deletePost, name='delete-post'),
    path('update-vote-post/<int:id>/', views.updateVotePost, name='update-vote-post'),
    path('save-post/<int:id>/', views.savePost, name='save-post'),
    
    path('create-comment/<int:id>/', views.createComment, name='create-comment'),
    path('edit-comment/<int:id>/', views.editComment, name='edit-comment'),
    path('delete-comment/<int:id>/', views.deleteComment, name='delete-comment'),
    path('update-vote-comment/<int:id>/', views.updateVoteComment, name='update-vote-comment'),
    
    path('get-search-results/', views.getSearchResults, name='get-search-results'),
]
