from blog.models import Post


def add_role_to_context(request):
    return {
        'role': str(request.user.groups.first()).lower()
    }


def add_my_posts_to_context(request):
    return {
        'my_posts_count': Post.objects.all().filter(author_id=request.user.id).filter(has_moderated=False).count()
    }