from django.db import migrations


def create_initial_account_tiers(apps, schema_editor):
    AccountTier = apps.get_model('imagesApp', 'AccountTier')

    AccountTier.objects.create(
        name='Basic',
        thumbnail_sizes=[{"x": 200, "y": 200}],
        include_image=False,
        generate_expiring_links=False,
    )

    AccountTier.objects.create(
        name='Enterprise',
        thumbnail_sizes=[{"x": 200, "y": 200}, {"x": 400, "y": 400}],
        include_image=True,
        generate_expiring_links=False,
    )

    AccountTier.objects.create(
        name='Premium',
        thumbnail_sizes=[{"x": 200, "y": 200}, {"x": 400, "y": 400}],
        include_image=True,
        generate_expiring_links=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('imagesApp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_account_tiers),
    ]
