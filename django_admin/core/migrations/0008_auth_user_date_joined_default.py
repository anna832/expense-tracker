from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_expense_core_expense_amount_positive"),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE auth_user ALTER COLUMN date_joined SET DEFAULT now();",
            reverse_sql="ALTER TABLE auth_user ALTER COLUMN date_joined DROP DEFAULT;",
        ),
    ]
