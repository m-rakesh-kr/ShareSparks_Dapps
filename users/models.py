from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from cloudinary.models import CloudinaryField


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    contact_number = PhoneNumberField(unique=True, null=True, blank=True)
    wallet_address = models.CharField(max_length=100, null=True, unique=True)
    profile_image = CloudinaryField('image', folder='ShareSparks-ProfileImages',
                                    default='v1674627358/ShareSparks-ProfileImages/lj5keix6haboaxsoxsx9.jpg')

    REQUIRED_FIELDS = ["first_name", "last_name"]


