# Generated by Django 3.0.8 on 2020-07-25 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_auto_20200725_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profilepic',
            field=models.ImageField(blank=True, default='avatar.png', upload_to=''),
        ),
    ]
