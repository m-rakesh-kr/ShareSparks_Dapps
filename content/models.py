from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


# Create your models here.
class ContentCategory(models.Model):
    """
    Model for Content Category
    """
    category = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        self.category = self.category.upper()
        super().save(*args, **kwargs)


class Rewards(models.Model):
    """
    Model for Rewards
    """

    class Meta:
        unique_together = [['target', 'target_type']]

    token = models.FloatField(validators=[MinValueValidator(0)])
    target = models.PositiveIntegerField()
    reward_badge = CloudinaryField('image', folder='ShareSparks-Rewards',
                                   default='v1677652935/ShareSparks-Rewards/jgmg1lis3yefnqzjpzoz.png')

    CHOICES = [
        ('like', 'LIKE'),
        ('comment', 'COMMENT')
    ]

    target_type = models.CharField(max_length=7, choices=CHOICES)


class Content(models.Model):
    """
    Model for Content
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_updated = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    ipfs_address = models.CharField(max_length=320)
    category = models.ForeignKey(ContentCategory, on_delete=models.PROTECT)


class Likes(models.Model):
    """
    Model for liking in content
    """
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class Comments(models.Model):
    """
    Model for commenting on any content
    """
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.CharField(max_length=100)
    date_commented = models.DateField(auto_now_add=True)


class ContentVersion(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    ipfs_address = models.CharField(max_length=320)
    version_number = models.IntegerField()


class ContentRewards(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    reward = models.ForeignKey(Rewards, on_delete=models.CASCADE)
    is_rewarded = models.BooleanField(default=False)
    transaction_link = models.CharField(max_length=100)

    class Meta:
        unique_together = [['content', 'reward']]
