# Generated by Django 4.2.5 on 2023-11-03 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_stockquote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='company',
            field=models.CharField(help_text='The name of the company that issued the stock.', max_length=255),
        ),
    ]
