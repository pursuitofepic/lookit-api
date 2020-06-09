# Generated by Django 3.0.5 on 2020-06-09 14:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("studies", "0066_new-lab-study-perms-data-migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="lab",
            name="requested_researchers",
            field=models.ManyToManyField(
                blank=True,
                help_text="The Users who have requested to join this Lab.",
                related_name="requested_labs",
                related_query_name="requested_lab",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
