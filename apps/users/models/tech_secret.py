from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from typing_extensions import Final

from apps.common.models import BaseModel
from .user import User


class TechSecret(BaseModel):
    """
    Модель технического секрета.
    Включает в себя поле секрета, которое может использоваться для аутентификации внешних систем.
    """
    SECRET_HASH_LENGTH: Final[int] = 64

    secret_hash = models.CharField(
        max_length=SECRET_HASH_LENGTH,
        verbose_name=_("Secret Hash"),
        help_text=(
            "Секреты генерируются суперпользователем (не вводятся с клавиатуры!). Могут использоваться в качестве "
            "дополнительного фактора аутентификации технических учётных записей (добавляем секрет в полезную нагрузку JWT). "
            "Хранятся в виде хэшей (алгоритм `SHA256`). В открытом виде они предоставляются суперпользователю "
            "один раз - при генерации через админ-панель. Повторно увидеть секрет в открытом виде не получится "
            "- только генерировать заново."
        ),
        null=False,
        blank=False,
        unique=True,
        validators=[MinLengthValidator(SECRET_HASH_LENGTH)],
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Secret Owner"),
        related_name="tech_secret",
    )

    class Meta:
        verbose_name = _("Technical Secret")
        verbose_name_plural = _("Technical Secrets")

    def clean(self):
        super().clean()
        self.user: User
        if not self.user or self.user.type != User.Type.TECHNICAL:
            raise ValidationError(
                f"Создать секрет можно только для пользователей с "
                f"типом `{User.Type.TECHNICAL.label}`"
            )
