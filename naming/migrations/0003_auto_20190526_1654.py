# Generated by Django 2.2.1 on 2019-05-26 16:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0002_auto_20190526_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='branch',
            field=models.CharField(default='master', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='repository',
            name='name',
            field=models.CharField(default='sander/naming-test', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='syncmapping',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mappings', to='naming.Repository'),
        ),
    ]