from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Category, Expense


class CategoryModelTest(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name="Еда")

        self.assertEqual(category.name, "Еда")
        self.assertIsNotNone(category.id)

    def test_category_str(self):
        category = Category.objects.create(name="Еда")

        self.assertEqual(str(category), "Еда")


class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.category = Category.objects.create(name="Еда")

    def test_create_expense(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount_cents=50000,
            spent_at=date(2026, 8, 15),
            comment="Обед",
        )

        self.assertEqual(expense.user, self.user)
        self.assertEqual(expense.category, self.category)
        self.assertEqual(expense.amount_cents, 50000)
        self.assertEqual(expense.spent_at, date(2026, 8, 15))
        self.assertEqual(expense.comment, "Обед")

    def test_expense_str(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount_cents=50000,
            spent_at=date(2026, 8, 15),
            comment="Обед",
        )

        self.assertIn("Еда", str(expense))

    def test_expense_default_comment(self):
        expense = Expense.objects.create(
            user=self.user,
            category=self.category,
            amount_cents=50000,
            spent_at=date(2026, 8, 15),
        )

        self.assertEqual(expense.comment, "")
