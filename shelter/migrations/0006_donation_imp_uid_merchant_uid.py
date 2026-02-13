# Generated migration for PortOne payment tracking

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelter', '0005_alter_shelter_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='imp_uid',
            field=models.CharField(blank=True, max_length=64, verbose_name='포트원 결제고유번호'),
        ),
        migrations.AddField(
            model_name='donation',
            name='merchant_uid',
            field=models.CharField(blank=True, max_length=128, verbose_name='주문번호'),
        ),
    ]
