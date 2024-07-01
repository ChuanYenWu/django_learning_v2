from django.db import models
from django.urls import reverse
import uuid

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=20, help_text='Enter product name')
    summary = models.TextField(default="summary", max_length=100, help_text="Enter product summary")
    cost = models.IntegerField(help_text='Enter product cost')

    # Metadata
    class Meta:
        ordering = ['id']

    # Methods
    def get_absolute_url(self):
        """Returns the URL to access a particular instance of MyModelName."""
        return reverse('product-detail', args=[str(self.id)])

    def __str__(self):
        return self.name

class Order(models.Model):
    uuid = models.UUIDField( default=uuid.uuid4,
                          help_text="Unique ID for Buy Info")
    buyer = models.CharField(max_length=20, help_text='Enter customer name')
    phone = models.CharField(max_length=10, help_text='Enter customer phone number')
    total_cost = models.IntegerField(help_text='Enter total cost')
    #purchase_date = models.DateTimeField(auto_now_add=True)
    buytime = models.DateTimeField(null=True, blank=True)

    # Metadata
    class Meta:
        ordering = ['id']
    
    # Methods
    #def get_absolute_url(self):
    #    """Returns the URL to access a particular instance of MyModelName."""
    #    return reverse('buying-detail', args=[str(self.id)])

    def __str__(self):
        #return self.customer_name + "訂單"
        return f'Order {self.id}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'