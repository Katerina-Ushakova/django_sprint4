from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models.base import Model as Model
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.views.generic import (
    ListView,
    UpdateView,
    DeleteView,
    DetailView,
    CreateView)

from .forms import PostForm, CommentForm, UserForm
from .models import Post, Category
from .mixin import (
    CommentMixin,
    CommentSuccessUrlMixin,
    OnlyAuthorMixin,
    PostFormMixin,
    PostMixin
)

User = get_user_model()


class IndexListView(ListView):
    """Главная страница со списком постов."""

    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return Post.published_posts.all()


class CategoryPostsListView(ListView):
    """Страница со списком постов выбранной категории."""

    template_name = 'blog/category.html'
    paginate_by = 10

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
            created_at__lte=timezone.now()
        )

    def get_queryset(self):
        return self.get_category().posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=models.Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class DetailPostView(LoginRequiredMixin, DetailView):
    """Страница выбранного поста."""

    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post_id = self.kwargs.get(self.pk_url_kwarg)
        return (
            get_object_or_404(
                Post.objects.filter(
                    Q(pk=post_id)
                    & Q(author=self.request.user)
                    | Q(pk=post_id)
                    & Q(is_published=True)
                    & Q(category__is_published=True)
                    & Q(pub_date__lte=timezone.now())
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object()
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.all()
        return context


class CreatePostView(PostMixin, PostFormMixin, CreateView):
    """Создание поста."""

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class UpdatePostView(OnlyAuthorMixin, PostMixin, PostFormMixin, UpdateView):
    """Редактирование поста."""

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.object.pk}
        )


class DeletePostView(OnlyAuthorMixin, PostMixin, DeleteView):
    """Удаление поста."""

    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post,
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context


class CreateCommentView(CommentSuccessUrlMixin, CreateView):
    """Создание комментария."""

    pk_url_kwarg = 'post_id'
    form_class = CommentForm

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post,
            pk=self.kwargs.get(self.pk_url_kwarg)
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.get_object()
        return super().form_valid(form)


class UpdateCommentView(CommentMixin, CommentSuccessUrlMixin, UpdateView):
    """Редактирование комментария."""

    form_class = CommentForm


class DeleteCommentView(CommentMixin, CommentSuccessUrlMixin, DeleteView):
    """Удаление комментария."""

    pass


class ProfileListView(ListView):
    """Страница со списком постов пользователя."""

    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_profile(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        if self.request.user == self.get_profile():
            return Post.objects.filter(
                author=self.get_profile()
            ).annotate(
                comment_count=models.Count('comments')
            ).order_by('-pub_date')
        else:
            return Post.published_posts.filter(
                author=self.get_profile()
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
        return context


@login_required
def edit_profile(request):
    """Редактирование страницы пользователя"""
    template = 'blog/user.html'
    instance = request.user or None
    form = UserForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    context = {'form': form}
    return render(request, template, context)
