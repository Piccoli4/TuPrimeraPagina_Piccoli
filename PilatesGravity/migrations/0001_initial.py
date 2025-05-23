# Generated by Django 5.2.1 on 2025-05-18 15:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('dia', models.CharField(max_length=20)),
                ('hora', models.TimeField()),
                ('cupo_maximo', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('apellido', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefono', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('confirmado', models.BooleanField(default=False)),
                ('clase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PilatesGravity.clase')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PilatesGravity.cliente')),
            ],
        ),
    ]
