# Generated by Django 5.1.6 on 2025-02-18 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comparisons', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comparison',
            name='title',
            field=models.CharField(blank=True, max_length=255, verbose_name='Название'),
        ),
    ]
