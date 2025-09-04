from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('title',)


class Location(models.Model):
    name = models.CharField(max_length=256)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ← добавь

    class Meta:
        ordering = ('name',)


class Post(models.Model):
    title = models.CharField(max_length=256)
    text = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now, help_text='Дата публикации')
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True)

    class Meta:
        ordering = ('-pub_date', '-created_at')

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'
