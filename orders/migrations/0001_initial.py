from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('shop', '0001_initial'), ('users', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('state', models.CharField(choices=[('new','Новый'),('confirmed','Подтверждён'),('assembled','Собран'),('sent','Отправлен'),('delivered','Доставлен'),('canceled','Отменён')], default='new', max_length=20)),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='shop.contact')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='users.user')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='orders.order')),
                ('product_info', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.productinfo')),
            ],
        ),
        migrations.AddConstraint(
            model_name='orderitem',
            constraint=models.UniqueConstraint(fields=('order', 'product_info'), name='unique_order_item'),
        ),
    ]
