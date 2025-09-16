# AppTienda/views_category.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Category
from .forms import CategoryForm
from .decorators import can_manage_required, user_can_manage


def _paginate(request, qs, per_page=10):
    p = Paginator(qs, per_page)
    return p.get_page(request.GET.get("page"))


@login_required(login_url="login")
def categories_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Category.objects.all().order_by("name")
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    page_obj = _paginate(request, qs, per_page=10)
    ctx = {
        "title": "Categorías",
        "page_obj": page_obj,
        "query": q,
        "can_manage": user_can_manage(request.user),
    }
    return render(request, "AppTienda/categories/list.html", ctx)


@login_required(login_url="login")
@can_manage_required
def categories_add(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Categoría creada.")
        return redirect("categories_list")
    return render(request, "AppTienda/categories/form.html", {"title": "Nueva categoría", "form": form})


@login_required(login_url="login")
@can_manage_required
def categories_edit(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Categoría actualizada.")
        return redirect("categories_list")
    return render(request, "AppTienda/categories/form.html", {"title": f"Editar categoría #{pk}", "form": form})


@login_required(login_url="login")
@can_manage_required
def categories_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Categoría eliminada.")
        return redirect("categories_list")
    return render(
        request,
        "AppTienda/categories/confirm_delete.html",
        {"title": f"Eliminar categoría #{pk}", "object": obj},
    )
