from .models import SiteInfo,SymbolOfTrust,SeoWebSite,PromotionalCardProduct
from shop.models import BrandCategory


def site_info_context(request):
    site_info=SiteInfo.objects.all().first()
    if site_info:
        return {
            'site_info':site_info
        }
    else:
        return {
            'site_info':None
        }
    


def symbol_of_trust_context(request):   
    sot = SymbolOfTrust.objects.first()
    if sot:
        return{
            'sot':sot
        }
    else:return {
        'sot':None
    }

def top_brands(request):
    list_barnds = []

    for b in BrandCategory.objects.all():
        if b.image:
            list_barnds.append(b.pk)
        
    if list_barnds:
        return {
            'brands':BrandCategory.objects.filter(id__in=list_barnds)[:5]
        }
    else:
        return{
            'brands':None
        }

    
def website_seo(request):
    return {
        'web_seo':SeoWebSite.objects.all()
    }
    


def promotional_card_product(request):
    return {
        'promotional_products':PromotionalCardProduct.objects.all().first()
    }