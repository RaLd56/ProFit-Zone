from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.auth.models import User


class Product(PolymorphicModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    popularity = models.IntegerField(default=0)
    img = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} в корзине {self.cart.user.username}"

    def get_total_price(self):
        return self.quantity * self.product.price


class SwedishWall(Product):  
    in_bundle = models.TextField(help_text="Список товаров в комплекте")
    installation_type = models.CharField(max_length=255)
    max_load = models.CharField(max_length=100)
    material = models.CharField(max_length=255)
    dimensions = models.TextField(help_text="Габариты в см")
    packaging_parameters = models.TextField(help_text="Параметры упаковки")
    bar_diameter = models.CharField(max_length=100)
    distance_between = models.CharField(max_length=100)
    warranty = models.CharField(max_length=100)
    color = models.CharField(max_length=30)

class HorizontalBar(Product): 
    in_bundle = models.TextField(help_text="Список товаров в комплекте")
    installation_type = models.CharField(max_length=255)
    max_load = models.CharField(max_length=100)
    material = models.CharField(max_length=255)
    dimensions = models.TextField(help_text="Габариты в см")
    packaging_parameters = models.TextField(help_text="Параметры упаковки")
    bar_diameter = models.CharField(max_length=100)
    distance_between = models.CharField(max_length=100)
    warranty = models.CharField(max_length=100)
    color = models.CharField(max_length=30)

class Nutrition(Product): 
    category = models.CharField(max_length=100)
    calories = models.PositiveIntegerField()
    protein = models.DecimalField(max_digits=5, decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2)
    fats = models.DecimalField(max_digits=5, decimal_places=2)
    serving_size = models.CharField(max_length=50)
    flavor = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class WeightliftingProduct(Product):  
    category = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    material = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class FitnessProduct(Product):  
    category = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name