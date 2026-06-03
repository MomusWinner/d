from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Name of role")

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255)


class PickupPoint(models.Model):
    address = models.TextField()

    def __str__(self) -> str:
        return self.address[:50]


class Supplier(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=20, default="шт.")
    article = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places = 2, default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    manufacturer = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quantity = models.IntegerField()
    description = models.TextField()
    photo = models.ImageField(upload_to='products/', null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            this = Product.objects.get(id=self.id)
            if this.photo and self.photo and this.photo != self.photo:
                this.photo.delete(save=False)
        except:
            pass

        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.price * (1 - self.discount / 100) if self.discount else self.price
    
    def __str__(self) -> str:
        return f"{self.article} - {self.name}"


STATUS_CHOICES = [
    ('new', 'Новый'),
    ('сompleted', 'Завершен'),
]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateTimeField() #auto_now_add=True
    delivery_date = models.DateTimeField()
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="Новый")
    pickup_code = models.IntegerField()


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField()