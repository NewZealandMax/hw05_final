from django.core.paginator import Paginator

from yatube.settings import POSTS_PER_PAGE


def paginator(post_list, request):
    '''Returns page object.'''
    return Paginator(
        post_list, POSTS_PER_PAGE).get_page(request.GET.get('page'))
