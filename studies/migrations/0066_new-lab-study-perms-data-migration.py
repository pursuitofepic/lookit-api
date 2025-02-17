# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-05-13 15:53
from __future__ import unicode_literals

from django.db import migrations

from studies.permissions import LabGroup, SiteAdminGroup, StudyGroup


def add_all_permissions():
    """Enforce loading of perms

    See:
    https://stackoverflow.com/questions/29296757/django-data-migrate-permissions
    https://code.djangoproject.com/ticket/23422
    """
    from django.apps import apps
    from django.contrib.auth.management import create_permissions

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None


def _create_groups(
    model_instance, group_enum, group_class, perm_class, group_object_permission_model
):
    uuid_segment = str(model_instance.uuid)[:7]
    object_name = model_instance._meta.object_name
    unique_group_tag = (
        f"{object_name} :: {model_instance.name[:7]}... ({uuid_segment}...)"
    )

    for group_spec in group_enum:
        # Group name is going to be something like "READ :: Lab :: MIT (0235dfa...)
        group_name = f"{group_spec.name} :: {unique_group_tag}"
        group = group_class.objects.create(name=group_name)

        for permission_meta in group_spec.value:
            permission = perm_class.objects.get(codename=permission_meta.codename)

            group_object_permission_model.objects.create(
                content_object=model_instance, permission=permission, group=group
            )
            group.save()

        setattr(model_instance, f"{group_spec.name.lower()}_group", group)

    model_instance.save()


def apply_migration(apps, schema_editor):
    """Lab group changes.

    Args:
        apps: instance of django.apps.registry.Apps
        schema_editor: instance of django.db.backends.base.schema.BaseDatabaseSchemaEditor

    Side Effects:
        Adds the single MIT Lab construct, along with associated groups.
    """
    # Enforce loading of perms from intermediate migrations, see:
    # https://stackoverflow.com/questions/29296757/django-data-migrate-permissions
    # https://code.djangoproject.com/ticket/23422
    add_all_permissions()
    # Treat this like module scope, since we can't import and have to deal with historical
    # models.
    Lab = apps.get_model("studies", "Lab")
    Study = apps.get_model("studies", "Study")
    User = apps.get_model("accounts", "User")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    StudyGroupObjectPermission = apps.get_model("studies", "StudyGroupObjectPermission")
    LabGroupObjectPermission = apps.get_model("studies", "LabGroupObjectPermission")

    if not Lab.objects.filter(name="Sandbox lab").exists():
        practice_lab = Lab(
            name="Sandbox lab",
            institution="Lookit",
            principal_investigator_name="Sample Name",
            contact_email="lookit+practice@mit.edu",
            contact_phone="(123) 456-7890",
            lab_website="https://lookit.mit.edu/",
            description="""This is a sample lab researchers are added to upon joining Lookit. You can make studies in 
                this lab to try Lookit out ahead of setting up your own lab account. However, you will not be able to 
                collect actual data from these studies - you will need to create or join a lab that is approved to 
                run studies on Lookit.""",
            irb_contact_info="""IRB contact information would go here for a real lab.""",
            approved_to_test=False,
        )
        practice_lab.save()

    if not Lab.objects.filter(name="Demo lab").exists():
        demo_lab = Lab(
            name="Demo lab",
            institution="Lookit",
            principal_investigator_name="Sample Name",
            contact_email="lookit+demo@mit.edu",
            contact_phone="(123) 456-7890",
            lab_website="https://lookit.mit.edu/",
            description="""This is a sample lab researchers are added to upon joining Lookit. It contains several demo
                studies you will be able to see.""",
            irb_contact_info="""IRB contact information would go here for a real lab.""",
            approved_to_test=False,
        )
        demo_lab.save()

    # Abstain from using QuerySet.create here; emulate what we'll need to do when these
    # group fields are non-nullable.
    if not Lab.objects.filter(name="Early Childhood Cognition Lab").exists():
        mit_eccl_lab = Lab(
            name="Early Childhood Cognition Lab",
            institution="MIT",
            principal_investigator_name="Laura Schulz",
            contact_email="eccl@mit.edu",
            contact_phone="(617) 324-4859",
            lab_website="http://eccl.mit.edu/",
            description="""We study how children construct a commonsense understanding of the physical and social world. 
                Current lab members are especially interested in how children generate new ideas and choose which problems 
                are worth working on.
                Research in the lab often addresses 1) how children figure out cause-and-effect relations so that they can 
                predict, explain, and themselves cause things to happen; 2) influences on curiosity and exploration; and 3) 
                how these abilities interact with social cognition to help children understand themselves and other people. 
                """,
            irb_contact_info="""Committee on the Use of Humans as Experimental Subjects, M.I.T., Room E25-143B, 77 
                Massachusetts Ave, Cambridge, MA 02139, phone 1-617-253-6787.""",
            approved_to_test=True,
        )

        mit_eccl_lab.save()
    # Have to save so that this can go in as content_object during execution
    # of assign_perm

    _create_groups(mit_eccl_lab, LabGroup, Group, Permission, LabGroupObjectPermission)
    _create_groups(practice_lab, LabGroup, Group, Permission, LabGroupObjectPermission)
    _create_groups(demo_lab, LabGroup, Group, Permission, LabGroupObjectPermission)

    researchers = User.objects.filter(is_researcher=True, is_active=True)
    practice_lab.researchers.add(*researchers)
    practice_lab.guest_group.user_set.add(*researchers)
    practice_lab.save()

    demo_lab.researchers.add(*researchers)
    demo_lab.readonly_group.user_set.add(*researchers)
    demo_lab.save()

    # Create study groups and set the lab of all studies to the practice lab temporarily (will need to move
    # manually to appropriate new lab)
    for study in Study.objects.all():
        _create_groups(study, StudyGroup, Group, Permission, StudyGroupObjectPermission)
        study.lab = practice_lab
        study.admin_group.user_set.add(study.creator)
        study.save()

    # TODO after transfer complete - delete all Organizations and org-related perm groups
    # - e.g. MIT_ORG_RESEARCHER/READ/ADMIN; MIT_<...>_STUDY_READ/ADMIN

    for group_spec in SiteAdminGroup:
        group_name = group_spec.name
        if not Group.objects.filter(name=group_name).exists():
            group = Group.objects.create(name=group_name)
        else:
            group = Group.objects.get(name=group_name)
            group.permissions.set(Permission.objects.none())
        for permission_meta in group_spec.value:
            permission = Permission.objects.get(codename=permission_meta.codename)
            # assign_perm(permission, group) # Can't do this because we don't have the "real" Group imported
            group.permissions.add(permission)
        group.save()


def revert_migration(apps, schema_editor):
    """Reverses the migration.

    Args:
        apps: instance of django.apps.registry.Apps
        schema_editor: instance of django.db.backends.base.schema.BaseDatabaseSchemaEditor
    """
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    Organization = apps.get_model("accounts", "Organization")
    StudyGroupObjectPermission = apps.get_model("studies", "StudyGroupObjectPermission")
    LabGroupObjectPermission = apps.get_model("studies", "LabGroupObjectPermission")

    # These should cascade, effectively killing the related permissions.
    Group.objects.filter(
        id__in=StudyGroupObjectPermission.objects.values_list("group_id", flat=True)
    ).delete()

    Permission.objects.filter(
        id__in=StudyGroupObjectPermission.objects.values_list(
            "permission_id", flat=True
        )
    ).delete()

    Group.objects.filter(
        id__in=LabGroupObjectPermission.objects.values_list("group_id", flat=True)
    ).delete()

    Group.objects.filter(name__in=[g.name for g in SiteAdminGroup]).delete()

    Permission.objects.filter(
        id__in=LabGroupObjectPermission.objects.values_list("permission_id", flat=True)
    ).delete()

    # Create a single Organization object
    Organization.objects.all().delete()
    # TODO: reset id sequence?
    org = Organization(name="MIT")
    org.save()


class Migration(migrations.Migration):
    dependencies = [("studies", "0065_new-lab-study-perms-model-defs")]

    operations = [migrations.RunPython(apply_migration, revert_migration)]
