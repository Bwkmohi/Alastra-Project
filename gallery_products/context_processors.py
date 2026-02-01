from .models import GalleryProducts
from .views import count_shop_gallery
from sellers.context_processors import default_shop_context

def count_shop_gallery_context_processors(request):
    return{
        'count_shop_gallery':count_shop_gallery(default_shop_context(request).get('shop_id'))
    }