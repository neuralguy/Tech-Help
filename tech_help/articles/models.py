from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from unidecode import unidecode
from django_ckeditor_5.fields import CKEditor5Field

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, blank=True)
    content = CKEditor5Field()
    image = models.ImageField(upload_to='articles/', verbose_name='Изображение', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор', null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    views = models.PositiveIntegerField(default=0, verbose_name='Просмотры')
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
            original_slug = self.slug
            counter = 1
            while Article.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('articles:article_detail', kwargs={'slug': self.slug})
    
    def average_rating(self):
        return self.ratings.aggregate(models.Avg('value'))['value__avg'] or 0
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name='Статья')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_date']
    
    def __str__(self):
        return f'Комментарий от {self.author.username} к {self.article.title}'

    def get_reaction_count(self):
        return self.reactions.aggregate(
            likes=models.Count('value', filter=models.Q(value=Reaction.LIKE)),
            dislikes=models.Count('value', filter=models.Q(value=Reaction.DISLIKE))
        )
    
    def get_user_reaction(self, user):
        if user.is_authenticated:
            reaction = self.reactions.filter(user=user).first()
            return reaction.value if reaction else 0
        return 0

class Reaction(models.Model):
    LIKE = 1
    DISLIKE = -1
    REACTION_TYPES = [
        (LIKE, 'Нравится'),
        (DISLIKE, 'Не нравится'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    value = models.SmallIntegerField(choices=REACTION_TYPES)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')
        verbose_name = 'Реакция'
        verbose_name_plural = 'Реакции'

    def __str__(self):
        return f"{self.user} -> {self.comment} ({self.value})"

class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings', verbose_name='Статья')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    value = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')
    
    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        unique_together = ['article', 'user']  # Один пользователь может оставить только одну оценку
    
    def __str__(self):
        return f'Оценка {self.value} от {self.user.username} для {self.article.title}'
