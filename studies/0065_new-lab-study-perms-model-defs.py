# Generated by Django 3.0.5 on 2020-06-05 17:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import studies.permissions
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0011_update_proxy_permissions"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("studies", "0064_upgrade_django_1_11_to_2_1"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lab",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uuid", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("name", models.CharField(max_length=255, unique=True)),
                ("institution", models.CharField(max_length=255)),
                ("principal_investigator_name", models.CharField(max_length=255)),
                (
                    "contact_email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="Contact Email"
                    ),
                ),
                (
                    "contact_phone",
                    models.CharField(max_length=255, verbose_name="Contact Phone"),
                ),
                ("lab_website", models.URLField(verbose_name="Lab Website")),
                ("description", models.TextField(blank=True)),
                ("irb_contact_info", models.TextField(blank=True)),
                ("approved_to_test", models.BooleanField(default=False)),
                (
                    "admin_group",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lab_to_administer",
                        to="auth.Group",
                    ),
                ),
                (
                    "researchers",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The Users who belong to this Lab. A user in this lab will be able to create studies associated with this Lab and can be added to this Lab's studies.",
                        related_name="labs",
                        related_query_name="lab",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "view_group",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lab_for_viewers",
                        to="auth.Group",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "permissions": studies.permissions.LabPermission,
            },
        ),
        migrations.AlterModelOptions(
            name="study",
            options={
                "ordering": ["name"],
                "permissions": studies.permissions.StudyPermission,
            },
        ),
        migrations.AlterField(  # to make this reversible, set study org default - otherwise we re-add a non-nullable field with no default
            model_name="study",
            name="organization",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="studies",
                related_query_name="study",
                to="accounts.Organization",
                default=1,
            ),
        ),
        migrations.RemoveField(model_name="study", name="organization"),
        migrations.AddField(
            model_name="study",
            name="admin_group",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="study_to_administer",
                to="auth.Group",
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="analysis_group",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="study_for_analysis",
                to="auth.Group",
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="design_group",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="study_to_design",
                to="auth.Group",
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="manager_group",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="study_to_manage",
                to="auth.Group",
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="preview_group",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="study_to_preview",
                to="auth.Group",
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="researcher_group",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="study_for_research",
                to="auth.Group",
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="submission_processor_group",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="study_for_submission_processing",
                to="auth.Group",
            ),
        ),
        migrations.AddField(
            model_name="study",
            name="lab",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="studies",
                related_query_name="study",
                to="studies.Lab",
            ),
        ),
        migrations.CreateModel(
            name="StudyUserObjectPermission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="studies.Study"
                    ),
                ),
                (
                    "permission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth.Permission",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("user", "permission", "content_object")},
            },
        ),
        migrations.CreateModel(
            name="StudyGroupObjectPermission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="studies.Study"
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="auth.Group"
                    ),
                ),
                (
                    "permission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth.Permission",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("group", "permission", "content_object")},
            },
        ),
        migrations.CreateModel(
            name="LabUserObjectPermission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="studies.Lab"
                    ),
                ),
                (
                    "permission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth.Permission",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("user", "permission", "content_object")},
            },
        ),
        migrations.CreateModel(
            name="LabGroupObjectPermission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "content_object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="studies.Lab"
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="auth.Group"
                    ),
                ),
                (
                    "permission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth.Permission",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "unique_together": {("group", "permission", "content_object")},
            },
        ),
    ]
