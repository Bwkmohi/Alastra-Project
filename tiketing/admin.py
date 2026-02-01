from django.contrib import admin
from .models import Tikets,ResponseToTiket,CategoryTiket



admin.site.register(Tikets)
admin.site.register(ResponseToTiket)
admin.site.register(CategoryTiket)