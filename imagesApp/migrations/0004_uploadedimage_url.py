# Generated by Django 4.2.5 on 2023-09-28 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagesApp', '0003_alter_accounttier_thumbnail_sizes'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedimage',
            name='url',
            field=models.URLField(null=True),
        ),
    ]
