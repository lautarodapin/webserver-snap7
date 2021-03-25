# Generated by Django 3.1.7 on 2021-03-25 17:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20210325_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='nombre',
            field=models.CharField(max_length=255, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='area',
            name='plc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='areas', to='app.plc', verbose_name='PLC'),
        ),
        migrations.AlterField(
            model_name='area',
            name='tag',
            field=models.ManyToManyField(blank=True, related_name='areas', to='app.Tag', verbose_name='Tag'),
        ),
        migrations.AlterField(
            model_name='fila',
            name='area',
            field=models.ForeignKey(help_text='DB desde el cual se lee', on_delete=django.db.models.deletion.CASCADE, related_name='filas', to='app.area', verbose_name='Area (DB)'),
        ),
    ]
