from .models import Images
from accaunts.models import UserAuthentication
from sellers.models import Shop


def create_user_and_shop_image():
    import random
    from django.db import transaction

    authed_user_men_images = list(Images.objects.filter(imgfor='authed_user', gender='MEN'))
    authed_user_women_images = list(Images.objects.filter(imgfor='authed_user', gender='WOMEN'))
    shop_images = list(Images.objects.filter(imgfor='shop'))

    user_authentication = UserAuthentication.objects.all()
    shops = Shop.objects.all()

    with transaction.atomic():
        for user in user_authentication:
            if not user.profile:
                if user.gender == 'MEN' and authed_user_men_images:
                    chosen_image = random.choice(authed_user_men_images)
                    user.profile.name = chosen_image.image.name
                    user.save()
                elif user.gender == 'WOMEN' and authed_user_women_images:
                    chosen_image = random.choice(authed_user_women_images)
                    user.profile.name = chosen_image.image.name
                    user.save()

        for shop in shops:
            if not shop.logo and shop_images:
                chosen_image = random.choice(shop_images)
                shop.logo.name = chosen_image.image.name
                shop.save()
