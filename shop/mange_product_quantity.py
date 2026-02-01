
from .models import Products
from reservations.models import Reservation


def product_quantity(id,qty):
    try:
        p=Products.objects.get(
            id = id
        )
        if p.qunat:
            p.qunat -= int(qty)
            p.save()
    except Products.DoesNotExist:
        pass


def cost_product_quantity(order_id):
    for r in Reservation.objects.filter(order__id=order_id):
        if r.quantity:
            product_quantity(
                r.product.id,
                r.quantity
            )