# Generated by Django 2.2.7 on 2019-11-30 22:38

from django.db import migrations

def apply_migration(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Group = apps.get_model("auth", "Group")
    Group.objects.using(db_alias).bulk_create(
        [Group(name="joueur"), Group(name="entraineur")]
    )

    # driver_group = Group.objects.using(db_alias).get(name="group1")
    # User = apps.get_model("users", "User")
    # users = User.objects.using(db_alias)
    # driver_group.user_set.add(*users)

def revert_migration(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["joueur", "entraineur"]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_attendance'),
    ]

    operations = [migrations.RunPython(apply_migration, revert_migration)]
