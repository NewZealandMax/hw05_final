from django import template

from posts.models import Post


register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})

@register.filter
def total_posts(author):
    return Post.objects.filter(author=author).count()
