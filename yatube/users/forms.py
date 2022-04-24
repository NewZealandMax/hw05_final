from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from posts.models import Post


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {'text': 'Введите текст', 'group': 'Выберите группу'}
        help_texts = {
            'text': 'Напишите свои мысли',
            'group': '(необязательно)'
        }
