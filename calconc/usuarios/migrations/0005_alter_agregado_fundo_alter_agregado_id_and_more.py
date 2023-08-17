# Generated by Django 4.2 on 2023-08-16 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_agregado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agregado',
            name='fundo',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='massa_especifica',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='pen_150_um',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='pen_1_20_mm',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='pen_2_40_mm',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='pen_300_um',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='pen_4_80_mm',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='pen_600_um',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='pen_6_30_mm',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='pen_75_um',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='agregado',
            name='umidade',
            field=models.FloatField(),
        ),
    ]
