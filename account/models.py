import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from utils.file import get_size, image_content_types
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Create your models here.


def validate_image_size(file):
    max_upload_size = get_size(2.5)
    if file.size > max_upload_size:
        raise ValidationError(
            _("%(value)s is larger than 2.5MB"),
            params={"value": file},
        )


def validate_image_content_type(file):
    content_types = image_content_types
    if file.content_type not in content_types:
        raise ValidationError(
            _("%(value)s is not the valid type"),
            params={"value": file.content_type},
        )


class UserManager(BaseUserManager):
    def create_user(self, email, password, **other_fields):
        user = User(email=email, **other_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must be assigned to is_staff=True"))
        elif other_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must be assigned to is_superuser=True"))

        return self.create_user(email, password, **other_fields)


class User(AbstractUser):
    first_name = None
    last_name = None
    username = None

    email = models.EmailField("email address", unique=True)
    password = models.CharField("password", max_length=128, blank=True)
    image = models.URLField(
        "avatar image url",
        blank=True,
    )
    TYPE_CHOICES = (
        ("base", "from_base"),
        ("google", "from_google"),
        ("trial", "from_trial"),
    )
    type = models.CharField(
        "type", choices=TYPE_CHOICES, blank=False, default="base", max_length=255
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Settings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    defaultExpanded = models.BooleanField(default=True)
    showExactTime = models.BooleanField(default=False)

    SORT_CHOICES = (
        ("updated", "updated ascending"),
        ("-updated", "updated descending"),
        ("created", "created ascending"),
        ("-created", "created descending"),
    )

    sortInfo = models.CharField(
        default="-updated", choices=SORT_CHOICES, max_length=255
    )

    LANGUAGE_CHOICES = (
        ("", "none"),
        ("en", "English"),
        ("zh-CN", "simplified Chinese"),
        ("zh-TW", "traditional Chinese"),
    )
    language = models.CharField(default="", choices=LANGUAGE_CHOICES, max_length=255)

    THEME_CHOICES = (
        ("", "none"),
        ("dark", "dark"),
        ("light", "light"),
        ("system", "system"),
    )
    theme = models.CharField(default="", choices=THEME_CHOICES, max_length=255)


@receiver(post_save, sender=User)
def create_settings(sender, instance, created, **kwargs):
    if created:
        setting = Settings.objects.create(user=instance)


if settings.DEBUG:

    from apscheduler.schedulers.background import BackgroundScheduler

    """
    每天刪除trial用戶
    """

    from datetime import datetime, timedelta, timezone
    from django.utils import timezone

    def delete_trial():
        expired = timezone.now() - timedelta(hours=2)
        User.objects.filter(type="trial").filter(date_joined__lt=expired).delete()

    """
    定时任务
    """
    scheduler = BackgroundScheduler()
    try:
        scheduler.add_job(
            delete_trial,
            "cron",
            hour=23,
            minute=59,
            second=59,
            id="delete_trial",
            replace_existing=True,
            timezone="UTC",
        )
        scheduler.start()
    except Exception as e:
        print(e)
        scheduler.shutdown()
