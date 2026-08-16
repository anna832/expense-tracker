from django.contrib import admin

from .models import Category, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "category",
        "amount_cents",
        "spent_at",
        "created_at",
    ]
    list_filter = ["category", "spent_at"]
    search_fields = ["comment", "category__name"]