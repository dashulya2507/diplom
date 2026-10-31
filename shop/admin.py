from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse

from .models import Category, Contact, Parameter, Product, ProductInfo, ProductParameter, Shop
from .services import import_shop_data
from .tasks import do_import


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'url', 'user')
    list_filter = ('state',)
    search_fields = ('name',)

    def get_urls(self):
        urls = super().get_urls()
        custom = [path('import-products/', self.admin_site.admin_view(self.import_products_view), name='shop-import-products')]
        return custom + urls

    def import_products_view(self, request):
        if request.method == 'POST':
            source = request.POST.get('source', 'data/shop1.yaml')
            do_import.delay(source)
            self.message_user(request, 'Задача импорта запущена.', messages.SUCCESS)
            return HttpResponseRedirect(reverse('admin:shop_shop_changelist'))
        context = {
            **self.admin_site.each_context(request),
            'title': 'Импорт товаров',
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/import_products.html', context)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('shops',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'shop', 'price', 'price_rrc', 'quantity')
    list_filter = ('shop',)
    search_fields = ('product__name', 'model')


admin.site.register(Parameter)
admin.site.register(ProductParameter)
admin.site.register(Contact)
