from .views import count_shop_collaborators
from sellers.context_processors import default_shop_context


def count_shop_collaborators_context_processors(request):
    shop_id = default_shop_context(request).get('shop_id')
    return {
        'count_shop_collaborators':count_shop_collaborators(shop_id)
    }