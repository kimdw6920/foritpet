from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelter', '0008_merge_20260308_chat_and_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='weight_kg',
            field=models.FloatField(default=1.0, verbose_name='포장 무게(kg)'),
        ),
    ]

