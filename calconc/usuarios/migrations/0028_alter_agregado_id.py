# Generated by Django 4.2.4 on 2023-09-09 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0027_alter_agregado_unique_together_alter_agregado_nome_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agregado',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]