from django import forms
from .models import Article, Category, Tag, Comment
from django_summernote.widgets import SummernoteWidget

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-gray-300 bg-white text-gray-900',
                'style': 'color: black;',
                'placeholder': 'Введите заголовок'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-lg border-gray-300 bg-white text-gray-900',
                'style': 'color: black;'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border-gray-300 bg-white text-gray-900',
                'style': 'color: black;',
                'rows': 10
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-input'
            })

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Напишите комментарий...'
        }) 