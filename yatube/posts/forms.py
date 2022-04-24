from django.forms import ModelForm

from posts.models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Введите текст',
            'group': 'Выберите группу',
            'image': 'Прикрепите картинку к посту',
        }
        help_texts = {
            'text': 'Напишите свои мысли',
            'group': '(необязательно)',
            'image': '(так будет красивее)',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Напишите ваше мнение',
        }
