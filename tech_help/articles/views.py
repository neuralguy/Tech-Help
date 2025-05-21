from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Article, Category, Rating, Comment, Reaction
from .forms import ArticleForm, CommentForm

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

def article_list(request):
    articles_list = Article.objects.all()
    # Фильтрация по категории
    category_slug = request.GET.get('category')
    if category_slug:
        articles_list = articles_list.filter(category__slug=category_slug)
    categories = Category.objects.all()

    items_per_page = 12
    paginator = Paginator(articles_list, items_per_page)

    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # Если 'page' не целое число, показываем первую страницу
        articles = paginator.page(1)
    except EmptyPage:
        # Если 'page' больше максимального, показываем последнюю страницу
        articles = paginator.page(paginator.num_pages)

    return render(request, 'articles/article_list.html', {
        'articles': articles,
        'categories': categories
    })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    average_rating = article.average_rating()
    comments = article.comments.all()

    # Добавляем реакции пользователя для каждого комментария
    for comment in comments:
        if request.user.is_authenticated:
            reaction = comment.reactions.filter(user=request.user).first()
            comment.user_reaction = reaction.value if reaction else 0
        else:
            comment.user_reaction = 0
            
    context = {
        'article': article,
        'average_rating': average_rating,
        'comments': comments,
    }
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(article=article, user=request.user).first()
        context['user_rating'] = user_rating
    
    return render(request, 'articles/article_detail.html', context)

@login_required
def add_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)
    comments = article.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            return redirect('articles:article_detail', slug=slug)
    return redirect('articles:article_detail', slug=slug)

@login_required
def delete_comment(request, slug, comment_id):
    try:
        article = Article.objects.get(slug=slug)
        comment = Comment.objects.get(article=article, id=comment_id)
        if request.user == comment.author or request.user.is_staff:
            comment.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False}, status=403)
    except Exception as e:
        print(f"Delete error: {str(e)}")
        return JsonResponse({'success': False}, status=500)

@login_required
def edit_comment(request, slug, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.author or request.user.is_staff:
        new_text = request.POST.get('text', '')
        comment.text = new_text
        comment.save()
        return JsonResponse({'success': True, 'new_text': comment.text})
    return JsonResponse({'success': False}, status=403)

@login_required
def handle_reaction(request, slug, comment_id):
    article = get_object_or_404(Article, slug=slug)
    comment = get_object_or_404(Comment, id=comment_id, article=article)
    value = int(request.POST.get('value'))
    
    reaction, created = Reaction.objects.update_or_create(
        user=request.user,
        comment=comment,
        defaults={'value': value}
    )
    
    counts = comment.get_reaction_count()
    return JsonResponse({
        'likes': counts['likes'] or 0,
        'dislikes': counts['dislikes'] or 0,
        'user_reaction': value
    })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

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
