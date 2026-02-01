from django.contrib import admin
from django.urls import path,include
from shop import views
from django.conf.urls.static import static
from . import settings
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps.views import sitemap
from shop.sitemaps import ProductSitemap,ProductBrandSitemap,ProductMainCategorySitemap,BlogSitemap
from adv.sitemaps import ProjectSitemap
sitemaps = {
    'products': ProductSitemap,
    'brand':ProductBrandSitemap,
    'main_category':ProductMainCategorySitemap,
    'blog':BlogSitemap,
    'project':ProjectSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    #seo
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    # Shop app urls
    path('',views.index,name='index'),
    path('product/<int:id>/<slug:slug>/',views.product_detail,name='product_detail'),
    path('products/<int:product_id>/price-history/', views.product_price_history, name='product_price_history'),
    path('category_view/',views.super_category,name='category_view'),
    path('products/',views.products_list,name='products_list'),
    path('products/filter/',views.filter_products,name='filter_products'),
    path('search_products/',views.search_products,name='search_products'),
    path('shops/best-shops/',views.best_shops,name='best_shops'),
    path('ajax/product-like/<int:product_id>/',views.like_or_dis_like_prodcut),
    path('main_category_detail/<slug:slug>/', views.main_category_detail,name='main_category_detail'),
    path('brand_detail/<int:id>/<slug:slug>/', views.brand_detail,name='brand_detail'),
    path('comment_add/<int:id>/',views.comment_add,name='comment_add'),
    path('super_category_products/<int:super_category_id>/<slug:slug>/',views.super_category_products,name='super_category_products'),

    path('api/main-categories/<int:super_category_id>/', views.get_main_categories, name='get_main_categories'),
    # 
    path('compare/',include('compare.urls')),
    # 
    path('adv/',include('adv.urls')),
    # 
    path('blogs/',include('blog.urls')),
    path('wallet/',include('walet.urls')),
    path('costs/',include('costs_fee.urls')),
    path('smartget-produtcs/',include('smartgtp.urls')),
    path('notifications/',include('notifications.urls')),
    path('follow/',include('follow.urls')),
    path('chat/',include('chat.urls')),
    path('accaunt/',include('accaunts.urls')),
    path('cart/',include('cart.urls')),
    path('copon/',include('copon2.urls')),
    path('questions/',include('question_response.urls')),
    path('site-manage/',include('siteinfo.urls')),
    path('zarin_pal/',include('zarinpal.urls')),
    path('reservation/',include('reservations.urls')),
    path('supporter/',include('supporter.urls')),
    path('watchlist/',include('watchlist.urls')),
    path('tiketing/',include('tiketing.urls')),
    path('facelogin/',include('facelogin.urls')),
    path('group_cart/',include('group_cart.urls')),
    path('response_tikets/',include('response_tikets.urls')),
    # Market Palec
    path('shop/',include('sellers.urls')),
    path('shop/coll/',include('collaborator.urls')),    
    path('shop/report_shop/',include('report_shop.urls')),    
    path('shop/shop_coupons/',include('shop_coupon.urls')),    
    path('shop/shop_orders/',include('shop_manage_order.urls')), 
    path('shop/shop_products/',include('shop_manage_products.urls')),     
    path('shop/product_videos/',include('product_videos.urls')),
    path('shop/story/',include('story.urls')),
    path('shop/shop_questions/',include('shop_questions.urls')),
    path('shop/gallery_products/',include('gallery_products.urls')),
    ]+static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
