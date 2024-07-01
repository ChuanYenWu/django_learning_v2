from django.contrib import admin
from .models import Product, Order, OrderItem
# Register your models here.
#admin.site.register(LunchboxModel)
#admin.site.register(BuyingModel)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','buyer', 'phone', 'total_cost', 'buytime')
    list_filter = ('phone', 'buytime')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order','product', 'quantity')
    list_filter = ('order',)