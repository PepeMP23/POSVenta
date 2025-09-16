from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F, FloatField
from django.db import transaction

from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Product, StockEntry, Sale, Customer, Category
from .forms import (
    LoginForm, UserForm, ProductForm, StockEntryForm, SaleForm,
    CustomerForm, CategoryForm
)
from .decorators import can_manage_required, user_can_manage

# ---------- Helpers ----------
def _paginate(request, qs, per_page=10):
    p = Paginator(qs, per_page)
    return p.get_page(request.GET.get("page"))

# ---------- Auth ----------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("dashboard")
    return render(request, "AppTienda/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada.")
    return redirect("login")

# ---------- Dashboard (fix de altura del gráfico) ----------
@login_required(login_url="login")
def dashboard(request):
    labels, series = [], []
    kpi = {"revenue": 0.0, "orders": 0, "customers": 0, "top_sell": {"name":"—","qty":0,"revenue":0.0,"price":0.0}}
    try:
        today = timezone.localdate()
        labels = [(today - timezone.timedelta(days=i)).strftime("%d %b") for i in range(29,-1,-1)]
        since = timezone.now() - timezone.timedelta(days=30)
        qs = Sale.objects.filter(created_at__gte=since)

        agg = qs.values("product","product__name","product__price").annotate(
            qty=Sum("quantity"),
            rev=Sum(F("quantity") * F("unit_price"), output_field=FloatField())
        )
        if agg:
            best = max(agg, key=lambda a: a.get("qty") or 0)
            kpi["top_sell"] = {
                "name": best["product__name"],
                "qty": int(best.get("qty") or 0),
                "revenue": round(best.get("rev") or 0.0, 2),
                "price": float(best.get("product__price") or 0.0),
            }

        rev_map = {lbl:0.0 for lbl in labels}
        day_sales = (qs.annotate(day=F("created_at__date"))
                       .values("day")
                       .annotate(rev=Sum(F("quantity") * F("unit_price"), output_field=FloatField())))
        for d in day_sales:
            lbl = d["day"].strftime("%d %b")
            if lbl in rev_map:
                rev_map[lbl] = float(d["rev"] or 0.0)
        series = [rev_map[lbl] for lbl in labels]

        kpi["revenue"] = round(sum(series), 2)
        kpi["orders"] = qs.count()
        kpi["customers"] = Customer.objects.count()
    except Exception:
        pass
    return render(request, "AppTienda/dashboard.html", {"labels": labels, "sales": series, "kpi": kpi})

# ---------- Users ----------
@login_required(login_url="login")
def users_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = User.objects.all().order_by('-id')
    if q:
        qs = qs.filter(Q(email__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(role__icontains=q))
    page_obj = _paginate(request, qs)
    headers = ["ID","Email","Nombre","Rol","Activo","Staff"]
    items = [{"id":u.id,"cells":[u.id,u.email,f"{u.first_name} {u.last_name}".strip(),getattr(u,'role',''),"Sí" if u.is_active else "No","Sí" if u.is_staff else "No"]} for u in page_obj.object_list]
    return render(request, "AppTienda/modules/list.html", {
        "title":"Usuarios","headers":headers,"items":items,"page_obj":page_obj,
        "add_name":"users_add","edit_name":"users_edit","delete_name":"users_delete",
        "can_manage": user_can_manage(request.user),
    })

@can_manage_required
def users_add(request):
    form = UserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Usuario creado."); return redirect("users_list")
    return render(request, "AppTienda/modules/form.html", {"title":"Nuevo usuario","form":form})

@can_manage_required
def users_edit(request, pk):
    obj = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Usuario actualizado."); return redirect("users_list")
    return render(request, "AppTienda/modules/form.html", {"title":f"Editar usuario #{pk}","form":form})

@can_manage_required
def users_delete(request, pk):
    obj = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        obj.delete(); messages.success(request, "Usuario eliminado."); return redirect("users_list")
    return render(request, "AppTienda/modules/confirm_delete.html", {"title":f"Eliminar usuario #{pk}"})


# ---------- Customers (separados) ----------
@login_required(login_url="login")
def customers_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Customer.objects.all().order_by('-id')
    if q:
        qs = qs.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(address__icontains=q)|Q(phone__icontains=q))
    page_obj = _paginate(request, qs)
    headers = ["ID","Nombre","Teléfono","Dirección"]
    items = [{"id":c.id,"cells":[c.id,f"{c.first_name} {c.last_name}".strip(),c.phone or "—",c.address or "—"]} for c in page_obj.object_list]
    return render(request, "AppTienda/modules/list.html", {
        "title":"Clientes","headers":headers,"items":items,"page_obj":page_obj,
        "add_name":"customers_add","edit_name":"customers_edit","delete_name":"customers_delete",
        "can_manage": user_can_manage(request.user),
    })

@can_manage_required
def customers_add(request):
    form = CustomerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cliente creado.")
        return redirect("customers_list")
    return render(request, "AppTienda/modules/form.html", {"title":"Nuevo cliente","form":form})

@can_manage_required
def customers_edit(request, pk):
    obj = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Cliente actualizado."); return redirect("customers_list")
    return render(request, "AppTienda/modules/form.html", {"title":f"Editar cliente #{pk}","form":form})

@can_manage_required
def customers_delete(request, pk):
    obj = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        obj.delete(); messages.success(request, "Cliente eliminado."); return redirect("customers_list")
    return render(request, "AppTienda/modules/confirm_delete.html", {"title":f"Eliminar cliente #{pk}"})


# ---------- Categories ----------
@login_required(login_url="login")
def categories_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Category.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q)|Q(description__icontains=q))
    page_obj = _paginate(request, qs)
    headers = ["ID","Nombre","Descripción","Creado"]
    items = [{"id":c.id,"cells":[c.id,c.name,c.description or "—",c.created_at]} for c in page_obj.object_list]
    return render(request, "AppTienda/modules/list.html", {
        "title":"Categorías","headers":headers,"items":items,"page_obj":page_obj,
        "add_name":"categories_add","edit_name":"categories_edit","delete_name":"categories_delete",
        "can_manage": user_can_manage(request.user),
    })

@can_manage_required
def categories_add(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Categoría creada."); return redirect("categories_list")
    return render(request, "AppTienda/modules/form.html", {"title":"Nueva categoría","form":form})

@can_manage_required
def categories_edit(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Categoría actualizada."); return redirect("categories_list")
    return render(request, "AppTienda/modules/form.html", {"title":f"Editar categoría #{pk}","form":form})

@can_manage_required
def categories_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete(); messages.success(request, "Categoría eliminada."); return redirect("categories_list")
    return render(request, "AppTienda/modules/confirm_delete.html", {"title":f"Eliminar categoría #{pk}"})


# ---------- Products (con category) ----------
@login_required(login_url="login")
def products_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Product.objects.select_related("category").all().order_by('-id')
    if q:
        qs = qs.filter(Q(name__icontains=q)|Q(description__icontains=q)|Q(category__name__icontains=q))
    page_obj = _paginate(request, qs)
    headers = ["ID","Nombre","Categoría","Precio","Stock"]
    items = [{"id":p.id,"cells":[p.id,p.name,(p.category.name if p.category else "—"),f"${p.price}",f"{p.stock}"]} for p in page_obj.object_list]
    return render(request, "AppTienda/modules/list.html", {
        "title":"Productos","headers":headers,"items":items,"page_obj":page_obj,
        "add_name":"products_add","edit_name":"products_edit","delete_name":"products_delete",
        "can_manage": user_can_manage(request.user),
    })

@can_manage_required
def products_add(request):
    form = ProductForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Producto creado."); return redirect("products_list")
    return render(request, "AppTienda/modules/form.html", {"title":"Nuevo producto","form":form})

@can_manage_required
def products_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Producto actualizado."); return redirect("products_list")
    return render(request, "AppTienda/modules/form.html", {"title":f"Editar producto #{pk}","form":form})

@can_manage_required
def products_delete(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        obj.delete(); messages.success(request, "Producto eliminado."); return redirect("products_list")
    return render(request, "AppTienda/modules/confirm_delete.html", {"title":f"Eliminar producto #{pk}"})


# ---------- Stock ----------
@login_required(login_url="login")
def stock_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = StockEntry.objects.select_related("product").all().order_by('-id')
    if q:
        qs = qs.filter(Q(product__name__icontains=q)|Q(note__icontains=q))
    page_obj = _paginate(request, qs)
    headers = ["ID","Producto","+Cantidad","Nota","Fecha"]
    items = [{"id":s.id,"cells":[s.id,s.product.name,f"+{s.quantity}",s.note or "—",s.created_at]} for s in page_obj.object_list]
    return render(request, "AppTienda/modules/list.html", {
        "title":"Entradas de Stock","headers":headers,"items":items,"page_obj":page_obj,
        "add_name":"stock_add","edit_name":None,"delete_name":"stock_delete",
        "can_manage": user_can_manage(request.user),
    })

@can_manage_required
@transaction.atomic
def stock_add(request):
    form = StockEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Stock agregado."); return redirect("stock_list")
    return render(request, "AppTienda/modules/form.html", {"title":"Nueva entrada de stock","form":form})

@can_manage_required
def stock_delete(request, pk):
    obj = get_object_or_404(StockEntry, pk=pk)
    if request.method == "POST":
        obj.delete(); messages.success(request, "Entrada de stock eliminada."); return redirect("stock_list")
    return render(request, "AppTienda/modules/confirm_delete.html", {"title":f"Eliminar entrada de stock #{pk}"})


# ---------- Sales ----------
@login_required(login_url="login")
def sales_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Sale.objects.select_related("product","customer").all().order_by('-id')
    if q:
        qs = qs.filter(
            Q(product__name__icontains=q) |
            Q(customer__first_name__icontains=q) |
            Q(customer__last_name__icontains=q)
        )

    page_obj = _paginate(request, qs)
    headers = ["ID","Producto","Cliente","Cantidad","Precio U.","Total","Fecha"]  # 👈 agregamos Total
    items = []
    for s in page_obj.object_list:
        cust = f"{s.customer.first_name} {s.customer.last_name}".strip() if s.customer else "—"
        items.append({
            "id": s.id,
            "cells": [
                s.id,
                s.product.name,
                cust,
                f"{s.quantity}",
                f"${s.unit_price:.2f}",
                f"${s.total_amount:.2f}",     # 👈 mostramos total guardado
                s.created_at,
            ],
        })

    return render(request, "AppTienda/modules/list.html", {
        "title":"Ventas","headers":headers,"items":items,"page_obj":page_obj,
        "add_name":"sales_add","edit_name":None,"delete_name":"sales_delete",
        "can_manage": user_can_manage(request.user),
    })


@can_manage_required
@transaction.atomic
def sales_add(request):
    form = SaleForm(request.POST or None)

    # Mapa id->precio para calcular total en el frontend
    products = Product.objects.all().values("id", "name", "price")
    price_map = {str(p["id"]): float(p["price"]) for p in products}

    if request.method == "POST" and form.is_valid():
        try:
            sale = form.save(commit=False)
            # snapshot del precio del producto (aunque el modelo ya lo hace)
            sale.unit_price = float(sale.product.price)
            sale.save()
            messages.success(request, "Venta registrada.")
            return redirect("sales_list")
        except Exception as e:
            messages.error(request, f"No se pudo registrar la venta: {e}")

    return render(
        request,
        "AppTienda/sales/form.html",
        {"title": "Nueva venta", "form": form, "price_map": price_map},
    )

@can_manage_required
def sales_delete(request, pk):
    obj = get_object_or_404(Sale, pk=pk)
    if request.method == "POST":
        obj.delete(); messages.success(request, "Venta eliminada."); return redirect("sales_list")
    return render(request, "AppTienda/modules/confirm_delete.html", {"title":f"Eliminar venta #{pk}"})
