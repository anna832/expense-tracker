from typing import ClassVar

from django.contrib import admin

from .models import Category, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = ["id", "name"]
    search_fields: ClassVar[list[str]] = ["name"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = ["id", "category", "amount_cents", "spent_at"]
    search_fields: ClassVar[list[str]] = ["comment"]
    list_filter: ClassVar[list[str]] = ["category", "spent_at"]
    list_select_related: ClassVar[list[str]] = ["category", "user"]
