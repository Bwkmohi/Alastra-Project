from .models import Category


def category_context(request):
    return {
        'category_context':Category.objects.all()[:5]
    }