from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    # Type annotation for autocomplete
    # (models.Model hasn't attribute objects statically).
    objects: models.Manager

    created_at = models.DateTimeField(
        db_index=True,
        default=timezone.now,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-updated_at",)
