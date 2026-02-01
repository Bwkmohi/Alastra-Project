from django.db import models
from django.contrib.auth.models import User
from accaunts.models import UserAuthentication
from sellers.models import Shop


class ShopCollaborator(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_authentication = models.ForeignKey(UserAuthentication, on_delete=models.CASCADE)
    # national_id_auth = models.ForeignKey(NationalIDAuthentication, on_delete=models.CASCADE,null=True,blank=True)

    # Product permissions
    can_see_products = models.BooleanField(default=False)
    can_add_product = models.BooleanField(default=False)
    can_delete_product = models.BooleanField(default=False)
    can_edit_product = models.BooleanField(default=False)

    # Message permissions
    can_see_comments_and_questions = models.BooleanField(default=False)
    can_response_questions = models.BooleanField(default=False)
    can_remove_comments = models.BooleanField(default=False)

    # Coupon permissions
    can_see_coupons = models.BooleanField(default=False)
    can_edit_coupon = models.BooleanField(default=False)
    can_add_coupon = models.BooleanField(default=False)
    can_remove_coupon = models.BooleanField(default=False)

    # Order permissions
    can_see_orders = models.BooleanField(default=False)
    can_edit_orders = models.BooleanField(default=False)

    # Collaborator permissions
    can_see_collaborators = models.BooleanField(default=False)
    can_edit_collaborators = models.BooleanField(default=False)
    can_add_collaborators = models.BooleanField(default=False)
    can_remove_collaborators = models.BooleanField(default=False)

    #Gallery Product permissions
    gallery_all_permissions = models.BooleanField(default=False)

    #Story permissions
    story_all_permissions = models.BooleanField(default=False)

    #Product Video permission]
    product_video_permissions = models.BooleanField(default=False)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shop', 'user')

    def __str__(self):
        return self.user.username
 

class CollaboratorActivity(models.Model):

    MODELS = [
        ('PRODUCTS',''),
        ('COUPON',''),
        ('COLLABRORATOR',''),
        ('PRODUCTS',''),
        ('PRODUCTS',''),
        ('PRODUCTS',''),

    ]
    ACTIVITY_CHOICES = [
        ('ADD', 'Add'),
        ('REMOVE', 'Remove'),
        ('EDIT', 'Edit'),
    ]
    shop_collaborator = models.ForeignKey(ShopCollaborator, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.CharField(max_length=200)
    activity_id = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shop_collaborator.user.username} - {self.activity_type} - {self.description}" 