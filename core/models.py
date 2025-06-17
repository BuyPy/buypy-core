from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteManager(models.Manager):
    """Soft Delete manager"""

    def get_queryset(self):
        """
        Getting queryset function for Soft Delete models.
        """
        return super().get_queryset().filter(deleted_at=None)


class SoftDeleteModel(models.Model):
    """
    Abstract model to model tables having soft-deletable objects
    """

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        """
        Delete function for soft deleting a model object instance.
        """
        self.deleted_at = timezone.now()
        self.save(*args, **kwargs)

    def hard_delete(self, *args, **kwargs):
        """
        Delete function for permanently deleting a model object instance.
        """
        super().delete(*args, **kwargs)

    def restore(self):
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True



