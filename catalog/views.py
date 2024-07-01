from django.shortcuts import render

# Create your views here.
import datetime
import os
from django.conf import settings
from .models import Product, Order, OrderItem
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
#from catalog.forms import BuyingModelForm, CheckOrderForm, UpdateForm_staff, UpdateForm_customer
from django import forms
from catalog.forms import OrderForm, OrderItemForm, BaseOrderItemFormSet
from catalog.forms import CheckOrderForm
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import BooleanField, Case, When, Value, F

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    #num_books = Book.objects.all().count()
    num_product = Product.objects.all().count()
    num_order = Order.objects.all().count()

    #jpbooks = Book.objects.filter(language__name__contains='japanese').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_product': num_product,
        'num_order': num_order,

        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class ProductListView(generic.ListView):
    model = Product
    paginate_by = 10

class ProductDetailView(generic.DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 在這裡添加你的額外參數
        if settings.STATIC_ROOT:
            image_path = os.path.join(settings.STATIC_ROOT, 'images', f'img_{self.object.id}.jpeg')
        else:
            image_path = os.path.join(settings.BASE_DIR, 'catalog', 'static', 'images', f'img_{self.object.id}.jpeg')
        
        image_exists = os.path.exists(image_path)
        #context['image_path'] = image_path
        context['image_exists'] = image_exists
        return context

#https://stackoverflow.com/questions/6069070/how-to-use-permission-required-decorators-on-django-class-based-views
@method_decorator(staff_member_required(login_url='login'), name='dispatch') #dispatch & Decorate
class OrderListView(generic.ListView):
    model = Order
    paginate_by = 10

    #def get_context_data(self, **kwargs):
        # 首先調用父類的 get_context_data 方法來獲得默認的上下文數據
    #    context = super().get_context_data(**kwargs)
        # 然後添加額外的上下文數據
    #    context['product_list'] = Product.objects.all()
        # 返回更新後的上下文數據
    #    return context

@method_decorator(staff_member_required(login_url='login'), name='dispatch') #dispatch & Decorate
class OrderDetailView(generic.DetailView):
    model = Order
    def get_object(self, queryset=None):
        return get_object_or_404(Order, uuid=self.kwargs.get('uuid'))

def neworder(request):
    ProductFormSet = forms.formset_factory(OrderItemForm, formset=BaseOrderItemFormSet, extra=0)
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        products = Product.objects.all()
        formset = ProductFormSet(request.POST, prefix='products')
        products_forms = zip(products, formset)
        #formset = ProductFormSet(request.POST, prefix='products', initial=[{'quantity': 0} for _ in products])
        if order_form.is_valid() and formset.is_valid():
            # 在這裡處理你的數據
            order = order_form.save(commit=False)
            total_cost = 0
            order.total_cost = total_cost
            order.save()  # 先保存 order 物件
            
            for product, form in zip(products, formset):
                quantity = form.cleaned_data.get('quantity')
                if quantity > 0:
                    total_cost += product.cost * quantity
                    #product = form.cleaned_data.get('name')
                    # 假設你已經有一個 Order 實例
                    #order = Order.objects.get(id=some_id)
                    OrderItem.objects.create(order=order, product=product, quantity=quantity)
            order.total_cost = total_cost
            order.buytime = datetime.datetime.now()
            order.save()

            # 從 POST 資料中取得 'next' 參數的值，如果沒有(會取得空字串)則預設為 'index'
            next_url = request.POST.get('next') or 'index'  
            #return HttpResponseRedirect(reverse(next_url))
            #使用redirect可以接受相對路徑和urls.py的名稱, 不需要reverse
            return redirect(next_url)
    else:
        order_form = OrderForm()
        products = Product.objects.all()
        #formset = ProductFormSet(initial=[{'name': p.name, 'summary': p.summary, 'cost': p.cost} for p in products], prefix='products')
        formset = ProductFormSet(initial=[{'quantity': 0} for _ in products], prefix='products')
        products_forms = zip(products, formset)

    context = {
    'order_form': order_form,
    'formset': formset,
    'products_forms': products_forms,
    }
    return render(request, 'catalog/neworder.html', context)

def checkorder(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = CheckOrderForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            
            request.session['phone_number'] = form.cleaned_data['phone']

            return HttpResponseRedirect(reverse('order_result'))
            
            # redirect to a new URL:

    # If this is a GET (or any other method) create the default form.
    else:
        
        form = CheckOrderForm()    

    context = {
        'form': form,
    }

    return render(request, 'catalog/checkorder.html', context)

def order_result(request):
    phone_number = request.session['phone_number']
    orderlist=Order.objects.filter(phone=phone_number).order_by('-id')
    #latest_uuid = orderlist.latest('id').uuid
    if orderlist:
        three_days_ago = datetime.date.today() - datetime.timedelta(days=3)

        orderlist = orderlist.annotate(
            intime=Case(
                When(buytime__gte=three_days_ago, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )

    paginator = Paginator(orderlist, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    #orderlist=page_obj

    context = {
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        #'orderlist': orderlist,
        #'latest_uuid': latest_uuid,
    }

    return render(request, 'catalog/order_result.html', context)

@staff_member_required(login_url='login')
def update_orderview_staff(request, uuid):
    order = get_object_or_404(Order, uuid=uuid)
    ProductFormSet = forms.formset_factory(OrderItemForm, formset=BaseOrderItemFormSet, extra=0)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        order_form = OrderForm(request.POST, instance=order)
        products = Product.objects.all()
        formset = ProductFormSet(request.POST, prefix='products')
        products_forms = zip(products, formset)
        #for form in formset:
        #    print(form['quantity'].value())
        
        # Check if the form is valid:
        if order_form.is_valid() and formset.is_valid():
            order = order_form.save(commit=False)
            total_cost = 0
            order.total_cost = total_cost
            order.save()  # 先保存 order 物件
            
            # Iterate over the formset and the products
            for product, form in zip(products, formset):
                quantity = form.cleaned_data.get('quantity')
                # Try to get the order item for the current product
                order_item = order.orderitem_set.filter(product=product).first()
                if quantity > 0:
                    total_cost += product.cost * quantity
                    if order_item is not None:
                        # If the order item exists and the quantity is greater than 0, update the quantity
                        order_item.quantity = quantity
                        order_item.save()
                    else:
                        # If the order item does not exist and the quantity is greater than 0, create a new order item
                        OrderItem.objects.create(order=order, product=product, quantity=quantity)
                elif order_item is not None:
                    # If the quantity is 0 and the order item exists, delete the order item
                    order_item.delete()

            order.total_cost = total_cost
            order.save()

                #return HttpResponseRedirect(reverse('orderlist'))
            next_url = request.POST.get('next') or 'order_detail'
            if next_url == 'order_detail':
                return redirect(next_url, uuid=order.uuid)
            else:
                return redirect(next_url)
        
    else:
        
        order_form = OrderForm(initial={'buyer': order.buyer,'phone': order.phone,})
        products = Product.objects.all()
        #formset = ProductFormSet(initial=[{'name': p.name, 'summary': p.summary, 'cost': p.cost} for p in products], prefix='products')
        initial_data = []
        for product in products:
            # 嘗試從order.orderitem_set中找到該產品
            order_item = order.orderitem_set.filter(product=product).first()
            if order_item is not None:
                # 如果找到了，則使用該產品的數量作為初始值
                initial_data.append({'quantity': order_item.quantity})
            else:
                # 如果沒有找到，則初始值為0
                initial_data.append({'quantity': 0})
        formset = ProductFormSet(initial=initial_data, prefix='products')
        #formset = ProductFormSet(initial=[{'quantity': 0} for product in products], prefix='products')
        products_forms = zip(products, formset)
    
    context = {
        'order_form': order_form,
        'formset': formset,
        'products_forms': products_forms,
    }

    return render(request, 'catalog/update_order_staff.html', context)

@staff_member_required(login_url='login')
def delete_orderview_staff(request, uuid):
    order = get_object_or_404(Order, uuid=uuid)

    if request.method == 'POST':
        order.delete()      #orderitem delete by cascade
        return redirect('orderlist')
    return render(request, 'catalog/order_confirm_delete.html', {'order': order})

def update_orderview_customer(request, uuid):
    order = get_object_or_404(Order, uuid=uuid)
    ProductFormSet = forms.formset_factory(OrderItemForm, formset=BaseOrderItemFormSet, extra=0)
    
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        
        # Create a form instance and populate it with data from the request (binding):
        order_form = OrderForm(request.POST, instance=order)
        products = Product.objects.all()
        formset = ProductFormSet(request.POST, prefix='products')
        products_forms = zip(products, formset)
        
        # Check if the form is valid:
        if order_form.is_valid() and formset.is_valid():
            
            if order.buytime.date() < datetime.date.today() - datetime.timedelta(days=3):
                form.add_error(None, ValidationError(_('已過期，不可修改')))
            #if order.buytime != datetime.date.today():
            #    raise ValidationError(_('已過期，不可修改'))
            else:
                order = order_form.save(commit=False)
                total_cost = 0
                order.total_cost = total_cost
                order.save()  # 先保存 order 物件


                # Iterate over the formset and the products
                for product, form in zip(products, formset):
                    quantity = form.cleaned_data.get('quantity')
                    # Try to get the order item for the current product
                    order_item = order.orderitem_set.filter(product=product).first()
                    if quantity > 0:
                        total_cost += product.cost * quantity
                        if order_item is not None:
                            # If the order item exists and the quantity is greater than 0, update the quantity
                            order_item.quantity = quantity
                            order_item.save()
                        else:
                            # If the order item does not exist and the quantity is greater than 0, create a new order item
                            OrderItem.objects.create(order=order, product=product, quantity=quantity)
                    elif order_item is not None:
                        # If the quantity is 0 and the order item exists, delete the order item
                        order_item.delete()
                order.total_cost = total_cost
                order.save()
                # request.session['phone_number'] should still exist
                return HttpResponseRedirect(reverse('order_result'))
        
    else:
        order_form = OrderForm(initial={'buyer': order.buyer,'phone': order.phone,})
        products = Product.objects.all()
        initial_data = []
        for product in products:
            # 嘗試從order.orderitem_set中找到該產品
            order_item = order.orderitem_set.filter(product=product).first()
            if order_item is not None:
                # 如果找到了，則使用該產品的數量作為初始值
                initial_data.append({'quantity': order_item.quantity})
            else:
                # 如果沒有找到，則初始值為0
                initial_data.append({'quantity': 0})
        formset = ProductFormSet(initial=initial_data, prefix='products')
        products_forms = zip(products, formset)
    context = {
        'order_form': order_form,
        'formset': formset,
        'products_forms': products_forms,
    }
    
    # seems OK to use same template with staff version
    return render(request, 'catalog/update_order_staff.html', context)
