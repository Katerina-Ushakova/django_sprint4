from django.db import models
from django.utils import timezone


class PublishedPostQuerySet(models.QuerySet):

    def publish_filter(self):
        return (self
                .select_related('author', 'category')
                .filter(
                    is_published=True,
                    pub_date__lte=timezone.now()
                ))

    def category_filter(self):
        return (self
                .publish_filter()
                .filter(category__is_published=True))

    def annotate_comment_count(self):
        return (self
                .prefetch_related('comments')
                .annotate(comment_count=models.Count('comments'))
                .order_by('-pub_date', 'title'))

    def all_filter(self):
        return self.category_filter().annotate_comment_count()


class PublishedPostManager(models.Manager):

    def get_queryset(self):
        return PublishedPostQuerySet(self.model, using=self._db)

    def publish_filter(self):
        return self.get_queryset().publish_filter()

    def category_filter(self):
        return self.get_queryset().category_filter()

    def annotate_comment_count(self):
        return self.get_queryset().annotate_comment_count()

    def all_filter(self):
        return self.get_queryset().all_filter()
