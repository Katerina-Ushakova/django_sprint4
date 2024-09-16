from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path(
        '',
        views.IndexListView.as_view(),
        name='index'
    ),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostsListView.as_view(),
        name='category_posts'
    ),
    path(
        'profile/<str:username>/',
        views.ProfileListView.as_view(),
        name='profile'
    ),
    path(
        'edit_profile/',
        views.edit_profile,
        name='edit_profile'
    ),
    path(
        'posts/<int:post_id>/',
        views.DetailPostView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/create/',
        views.CreatePostView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.UpdatePostView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.DeletePostView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/comment/',
        views.CreateCommentView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.UpdateCommentView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        views.DeleteCommentView.as_view(),
        name='delete_comment'
    ),
]
