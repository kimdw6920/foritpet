from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelter', '0009_product_weight_kg'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=64, verbose_name='송장번호'),
        ),
        migrations.AddField(
            model_name='donation',
            name='tracking_carrier',
            field=models.CharField(blank=True, max_length=64, verbose_name='택배사'),
        ),
        migrations.AddField(
            model_name='donation',
            name='shipped_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='발송일시'),
        ),
    ]
