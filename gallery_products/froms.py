from django import forms
from django.forms import inlineformset_factory
from .models import GalleryProducts, GalleryItem

class GalleryProductsForm(forms.ModelForm):
    class Meta:
        model = GalleryProducts
        fields = ['product']  # محصولات رو انتخاب می‌کنه

GalleryItemFormSet = inlineformset_factory(
    GalleryProducts, GalleryItem,
    fields=('image', 'caption'),
    extra=3,  # تعداد فرم‌های اضافه برای تصاویر
    can_delete=True
)
