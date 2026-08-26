from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "core_category"

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="expenses",
    )
    amount_cents = models.PositiveIntegerField()
    spent_at = models.DateField()
    comment = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "core_expense"

    def __str__(self):
        return f"{self.category} — {self.amount_cents}"
