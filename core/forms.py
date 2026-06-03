import random

from django import forms
from extra_views import InlineFormSetFactory

from .models import Product, Supplier, Order, OrderProduct
from django.forms import modelformset_factory

class ProductForm(forms.ModelForm):
    supplier_name = forms.CharField(label="Поставщик", required=True)

    class Meta:
        model = Product
        fields = [
            "article",
            "name",
            "unit",
            "price",
            "discount",
            "quantity",
            "description",
            "photo",
            "category",
            "manufacturer",
        ]
        labels = {
            "article": "Артикул",
            "name": "Название",
            "unit": "Единица измерения",
            "price": "Цена",
            "discount": "Скидка",
            "quantity": "Количество",
            "description": "Описание",
            "photo": "Фото",
            "category": "Категория",
            "manufacturer": "Производитель",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.supplier:
                self.fields["supplier_name"].initial = self.instance.supplier.name


    def save(self, commit=True):
        supplier, _ = Supplier.objects.get_or_create(
            name=self.cleaned_data["supplier_name"].strip()
        )

        instance = super().save(commit=False)
        instance.supplier = supplier

        if commit:
            instance.save()
        return instance
    
    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной")
        return price

    def clean_quantity(self):
        qty = self.cleaned_data.get("quantity")
        if qty < 0:
            raise forms.ValidationError("Количество не может быть отрицательным")
        return qty
    

class OrderForm(forms.ModelForm):
    pickup_code = forms.CharField(
        label="Код",
        required = True, 
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
        })
    )

    class Meta:
        model = Order
        fields = [
            "user",
            "pickup_point",
            "order_date",
            "delivery_date",
            "status",
        ]
        labels = {
            "user": "Пользователь",
            "order_date": "Дата заказа",
            "delivery_date": "Дата доставки",
            "status": "Статус",
            "pickup_point": "Пункт выдачи",

        }
        widgets = {
            "order_date": forms.DateTimeInput(attrs={
                'type': 'datetime-local',
            }),
            "delivery_date": forms.DateTimeInput(attrs={
                'type': 'datetime-local',
            }),
            "status": forms.Select(),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Новый объект
            self.fields["pickup_code"].initial = random.randint(1000, 9999)
        else:
            self.fields["pickup_code"].initial = self.instance.pickup_code

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.pickup_code = self.cleaned_data["pickup_code"].strip()
        if commit:
            instance.save()
        return instance


class OrderProductFormSet(InlineFormSetFactory):
    model = OrderProduct
    fields = ["product", "count"]
    factory_kwargs = {
        "extra": 1,
        "can_delete": True,
        "labels": {"product": "Продукт", "count": "Количество"}
    }