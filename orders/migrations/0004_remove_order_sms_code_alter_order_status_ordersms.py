# Generated by Django 4.1.1 on 2022-10-06 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_smshistory_order_sms_code_alter_order_activation_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='sms_code',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('sms pending', 'Sms Pending'), ('success', 'Success'), ('finished', 'Finished'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='sms pending', max_length=15),
        ),
        migrations.CreateModel(
            name='OrderSMS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sms_code', models.CharField(blank=True, max_length=255, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sms_codes', to='orders.order')),
            ],
        ),
    ]
