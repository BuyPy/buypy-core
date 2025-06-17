import uuid

from core.models import SoftDeleteModel, BaseModel
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class UserSoftDeleteModel(SoftDeleteModel):

    def hard_delete(self, *args, **kwargs):
        #TODO add task to delete all transactions
        super().hard_delete(*args, **kwargs)

    def restore(self):
        super().restore()
        DeleteUserRequest.objects.filter(user=self.user).delete()


class User(UserSoftDeleteModel, AbstractUser, BaseModel):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    first_name = None
    last_name = None
    username = None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        db_table = "users"


class DeleteUserRequest(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # delete_token = models.UUIDField(default=uuid.uuid4, editable=False) #TODO ?
    scheduled_time = models.DateField()

    class Meta:
        db_table = "delete_user_requests"
        ordering = ['scheduled_time']
        indexes = [
            models.Index(
                fields=["user_id", "scheduled_time"],
            )
        ]

    def create(self, *args, **kwargs):
        #TODO send delete email
        self.create(*args, **kwargs)

    def delete(self, *args, **kwargs):
        #TODO send cancel delete email
        self.delete(*args, **kwargs)
