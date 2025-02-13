from django.contrib import admin
from .models import Category, Tag, Article, Comment, Rating

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'updated_date', 'created_date']
    list_filter = ['created_date', 'updated_date']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_date'
    filter_horizontal = ('tags',)
    readonly_fields = ('views',)
    inlines = [CommentInline, RatingInline]

    def save_model(self, request, obj, form, change):
        if not change:  # Если создается новая статья
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'created_date', 'short_text')
    list_filter = ('created_date', 'author')
    search_fields = ('text', 'author__username', 'article__title')

    def short_text(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    short_text.short_description = 'Текст комментария'

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'value', 'created_date')
    list_filter = ('value', 'created_date')
    search_fields = ('user__username', 'article__title')
