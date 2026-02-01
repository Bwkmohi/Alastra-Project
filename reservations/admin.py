from django.contrib import admin
from .models import Reservation,OrderModel,ProvinceCategory,Citys


admin.site.register(ProvinceCategory)
admin.site.register(Reservation)
admin.site.register(Citys)


class ReservationsInline(admin.TabularInline):
    model = Reservation
    raw_id_fields = ['product']


@admin.register(OrderModel)
class AdminModel(admin.ModelAdmin):
    list_display = ['name','province','phone','paid']
    list_filter = ['paid','province','city',]
    inlines = [ReservationsInline]