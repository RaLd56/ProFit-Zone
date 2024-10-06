# Generated by Django 5.1.1 on 2024-10-06 16:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_cart_cartitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='FitnessProduct',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.product')),
                ('category', models.CharField(max_length=100)),
                ('material', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('main.product',),
        ),
    ]
