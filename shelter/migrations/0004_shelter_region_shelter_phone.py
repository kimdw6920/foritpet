# Generated migration for Shelter region and phone

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelter', '0003_product_remove_volunteerapplication_schedule_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shelter',
            name='region',
            field=models.CharField(choices=[('서울', '서울'), ('부산', '부산'), ('대구', '대구'), ('인천', '인천'), ('광주', '광주'), ('대전', '대전'), ('울산', '울산'), ('세종', '세종'), ('경기', '경기'), ('강원', '강원'), ('충북', '충북'), ('충남', '충남'), ('전북', '전북'), ('전남', '전남'), ('경북', '경북'), ('경남', '경남'), ('제주', '제주')], default='서울', max_length=20, verbose_name='지역'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='shelter',
            name='phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='연락처'),
        ),
        migrations.AlterField(
            model_name='shelter',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='shelters/', verbose_name='보호소이미지'),
        ),
        migrations.AlterField(
            model_name='shelter',
            name='target_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shelter.product', verbose_name='필요사료'),
        ),
    ]
