from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg
from .models import Article, Category, Tag, Comment, Rating
from .forms import ArticleForm, CommentForm

def article_list(request):
    articles = Article.objects.all().order_by('-created_date')
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    # Фильтрация по категории
    category_slug = request.GET.get('category')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    
    # Фильтрация по тегу
    tag_slug = request.GET.get('tag')
    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)
    
    # Пагинация
    paginator = Paginator(articles, 9)  # 9 статей на страницу
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    context = {
        'articles': articles,
        'categories': categories,
        'tags': tags,
        'current_category': category_slug,
        'current_tag': tag_slug,
    }
    return render(request, 'articles/article_list.html', context)

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    comments = article.comments.all().order_by('-created_date')
    user_rating = None
    
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(article=article, user=request.user).first()
    
    # Получаем среднюю оценку используя правильное имя поля
    average_rating = Rating.objects.filter(
        article=article
    ).aggregate(
        avg_rating=Avg('value')  # используем 'value' вместо 'rating'
    )['avg_rating']
    
    # Форматируем дату из правильного поля
    formatted_date = article.created_date.strftime("%d.%m.%Y") if article.created_date else None
    
    # Увеличиваем счетчик просмотров
    article.views += 1
    article.save()
    
    context = {
        'article': article,
        'comments': comments,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'formatted_date': formatted_date,
    }
    return render(request, 'articles/article_detail.html', context)

@login_required
def add_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('articles:article_detail', slug=slug)
    return redirect('articles:article_detail', slug=slug)

@login_required
def rate_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    if request.method == 'POST':
        value = request.POST.get('rating')
        if value:
            Rating.objects.update_or_create(
                article=article,
                user=request.user,
                defaults={'value': value}
            )
    
    return redirect('articles:article_detail', slug=slug)

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()  # Сохраняем теги
            messages.success(request, 'Статья успешно создана!')
            return redirect('articles:article_detail', slug=article.slug)
    else:
        form = ArticleForm()
    
    return render(request, 'articles/article_form.html', {
        'form': form,
        'title': 'Создать статью'
    })

@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    # Проверяем права на редактирование
    if article.author != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на редактирование этой статьи.')
        return redirect('articles:article_detail', slug=slug)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, 'Статья успешно обновлена!')
            return redirect('articles:article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'articles/article_form.html', {
        'form': form,
        'article': article,
        'title': 'Редактировать статью'
    })

@login_required
def article_delete(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    # Проверяем права на удаление
    if article.author != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав на удаление этой статьи.')
        return redirect('articles:article_detail', slug=slug)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Статья успешно удалена!')
        return redirect('articles:article_list')
    
    return render(request, 'articles/article_confirm_delete.html', {
        'article': article
    })
