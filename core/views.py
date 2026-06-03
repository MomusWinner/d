from decimal import Decimal
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import BaseDeleteView

from core.forms import OrderForm, OrderProductFormSet, ProductForm
from .models import OrderProduct, Product, Supplier, Order
from django.db.models import Q
from extra_views import CreateWithInlinesView, UpdateWithInlinesView


class UserLoginView(LoginView):
    template_name = "core/login.html"


class ProductListView(ListView):
    template_name = "core/product_list.html"
    model = Product
    context_object_name = "products"

    def get_queryset(self):
        queryset = Product.objects.all().select_related("supplier")
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(article__icontains=search_query)
                | Q(manufacturer__icontains=search_query)
                | Q(category__icontains=search_query)
            )

        supplier_id = self.request.GET.get("supplier", "")
        if supplier_id and supplier_id != "all":
            queryset = queryset.filter(supplier_id=supplier_id)

        # Фильтр по диапазону скидки
        discount_range = self.request.GET.get("discount_range", "")
        if discount_range:
            if discount_range == "0-12.99":
                queryset = queryset.filter(discount__gte=0, discount__lte=Decimal('12.99'))
            elif discount_range == "13-30":
                queryset = queryset.filter(discount__gte=13, discount__lte=30)
            elif discount_range == "30-100":
                queryset = queryset.filter(discount__gte=30, discount__lte=100)

        sort = self.request.GET.get("sort", "")
        if sort == "asc":
            queryset = queryset.order_by("quantity")
        elif sort == "desc":
            queryset = queryset.order_by("-quantity")
        return queryset
    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["suppliers"] = Supplier.objects.all()
        context["current_search"] = self.request.GET.get("search", "")
        context["current_supplier"] = self.request.GET.get("supplier", "")
        context["current_discount_range"] = self.request.GET.get("discount_range", "")
        context["current_sort"] = self.request.GET.get("sort", "")

        return context


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated
            and self.request.user.role
            and self.request.user.role.name == "admin"
        )


class ProductCreateUpdateMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_suppliers"] = Supplier.objects.all()
        return context
    

class ProductCreateView(AdminRequiredMixin, ProductCreateUpdateMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "core/product_form.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        messages.success(self.request, "Товар успешно добавлен")
        return super().form_valid(form)


class ProductUpdateView(AdminRequiredMixin, ProductCreateUpdateMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "core/product_form.html"
    success_url = reverse_lazy("product_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, "Товар успешно обновлен")
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("product_list")


class OrderListView(ListView):
    template_name = "core/order_list.html"
    model = Order
    context_object_name = "orders"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context
    

class OrderCreateView(CreateWithInlinesView):
    model = Order
    form_class = OrderForm
    inlines = [OrderProductFormSet]
    success_url = reverse_lazy("order_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        if self.inlines:
            context['formset'] = context['inlines'][0]
        return context  


class OrderUpdateView(UpdateWithInlinesView):
    model = Order
    form_class = OrderForm
    inlines = [OrderProductFormSet]
    success_url = reverse_lazy("order_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        if self.inlines:
            context['formset'] = context['inlines'][0]
        return context  


class OrderDeleteView(DeleteView):
    model = Order
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("order_list")