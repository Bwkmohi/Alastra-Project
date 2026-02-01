from .models import CostFeeSite


def cost_fee_context(request):
    try:
        return {'cost_fee':CostFeeSite.objects.filter(active = True)} 
    except CostFeeSite.DoesNotExist:
        return {}