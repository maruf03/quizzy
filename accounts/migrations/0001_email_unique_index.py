from django.db import migrations

SQL_CREATE = """
CREATE UNIQUE INDEX IF NOT EXISTS auth_user_email_ci_unique
ON auth_user (lower(email));
"""

SQL_DROP = """
DROP INDEX IF EXISTS auth_user_email_ci_unique;
"""

class Migration(migrations.Migration):
    dependencies = [
    ('accounts', '__first__'),
    ('auth', '0001_initial'),  # Ensure auth_user table exists before creating index
    ]

    operations = [
        migrations.RunSQL(SQL_CREATE, SQL_DROP),
    ]
