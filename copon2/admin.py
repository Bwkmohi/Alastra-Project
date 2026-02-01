from django.contrib import admin
from copon2.models import Coupon,SaveCoupon


admin.site.register(SaveCoupon)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'value', 'is_percent', 'active', 'used_count', 'usage_limit', 'valid_from', 'valid_to')
    list_filter = ('active', 'is_percent')
    search_fields = ('code',)