# Generated by Django 5.0.4 on 2024-05-19 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_app', '0002_remove_order_last_name_order_second_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='second_name',
            field=models.CharField(max_length=50, verbose_name='second_name'),
        ),
    ]