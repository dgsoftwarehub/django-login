# Generated by Django 4.1.1 on 2022-10-02 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_amount_alter_userbalance_amount_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SMSHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_data', models.JSONField()),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='sms_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='activation_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('sms pending', 'Sms Pending'), ('success', 'Success'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='sms pending', max_length=15),
        ),
    ]
