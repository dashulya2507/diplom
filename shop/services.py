import yaml
from pathlib import Path
from django.db import transaction
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

@transaction.atomic
def import_shop_data(source):
    if hasattr(source, 'read'):
        data = yaml.safe_load(source)
    elif str(source).startswith(('http://','https://')):
        import requests
        response=requests.get(source, timeout=20); response.raise_for_status(); data=yaml.safe_load(response.content)
    else:
        data=yaml.safe_load(Path(source).read_text(encoding='utf-8'))
    shop,_=Shop.objects.get_or_create(name=data['shop'])
    categories={}
    for item in data.get('categories',[]):
        cat,_=Category.objects.get_or_create(name=item['name']); cat.shops.add(shop); categories[item['id']]=cat
    for item in data.get('goods',[]):
        product,_=Product.objects.get_or_create(name=item['name'], category=categories[item['category']], defaults={'description': item.get('description','')})
        info, _ = ProductInfo.objects.update_or_create(
            product=product, shop=shop, external_id=item['id'],
            defaults={
                'model': item.get('model', ''),
                'quantity': item.get('quantity', 0),
                'price': item['price'],
                'price_rrc': item['price_rrc'],
            },
        )
        for name, value in item.get('parameters', {}).items():
            parameter, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.update_or_create(
                product_info=info, parameter=parameter, defaults={'value': str(value)}
            )
    return shop
