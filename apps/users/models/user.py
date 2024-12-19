from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model to extend built-in functionality."""

    class Type(models.IntegerChoices):
        DEFAULT = 1, _("Default")
        STAFF = 2, _("Staff")
        TECHNICAL = 3, _("Technical")

    type = models.PositiveSmallIntegerField(
        choices=Type.choices,
        default=Type.DEFAULT,
        verbose_name=_("User Type")
    )

    def __str__(self):
        str_type: str = self.get_type_display()  # type: ignore
        return f"{self.__class__.__name__}<{self.pk}, type={str_type}> {self.username}"

    def save(self, *args, **kwargs):
        # Устанавливаем тип для суперпользователя.
        if self.is_superuser and self.type == self.Type.DEFAULT:
            self.type = self.Type.STAFF
        super().save(*args, **kwargs)
