# Generated by Django 2.2.7 on 2020-09-03 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_comite_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_type',
            field=models.CharField(choices=[('BAR', 'Bar'), ('EAU', 'Eau'), ('LAVAGE_CHASUBLES', 'Lavage chasubles'), ('VESTIAIRE', 'Vestiaire'), ('BALLONS', 'Ballons'), ('LAVAGE_MAILLOTS', 'Lavage maillots'), ('TRACAGE_TERRAIN', 'Traçage terrain')], default=None, max_length=50, null=True, verbose_name='Type'),
        ),
    ]
