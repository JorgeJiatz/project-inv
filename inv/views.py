from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required, permission_required

from index.views import sinprivilegios
from .models import Categoria, SubCategoria, UnidadMedida, Marca, Producto
from .forms import  CategoriaForm, SubCategoriaForm, UMForm, MarcaForm, ProductoForm

# Create your views here.

class CategoriaView(sinprivilegios,\
                    generic.ListView):
    permission_required = "inv.view_categoria"
    model = Categoria
    template_name = "inv/categoria_list.html"
    context_object_name = "obj"


class CategoriaNew(SuccessMessageMixin, sinprivilegios, generic.CreateView):
    permission_required = "inv.add_categoria"
    model=Categoria
    template_name="inv/categoria_form.html"
    context_object_name="obj"
    form_class=CategoriaForm
    success_url=reverse_lazy("inv:categoria_list")
    success_message="Categoria Creada!"

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)


class CategoriaEdit(SuccessMessageMixin, sinprivilegios, generic.UpdateView):
    permission_required = "inv.change_categoria"
    model=Categoria
    template_name="inv/categoria_form.html"
    context_object_name="obj"
    form_class=CategoriaForm
    success_url=reverse_lazy("inv:categoria_list")
    success_message="Categoria Actualizada!"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)

@login_required(login_url='/login/')
@permission_required('inv.change_categoria', login_url='index:sin_privilegios')
def categoria_inactivar(request, id):
    ci = Categoria.objects.filter(pk=id).first()
    contexto={}
    template_name="inv/catalogos_del.html"


    if not ci:
        return redirect("inv:categoria_list")
    
    if request.method=='GET':
        contexto={'obj':ci}
    
    if request.method=='POST':
        ci.estado=False
        ci.save()
        messages.success(request, 'Categoria Inactivada')
        return redirect("inv:categoria_list")

    return render(request,template_name,contexto)
#class CategoriaDel(LoginRequiredMixin, generic.DeleteView):
    #model=Categoria
    #template_name='inv/catalogos_del.html'
    #context_object_name='obj'
    #success_url=reverse_lazy("inv:categoria_list")


class SubCategoriaView(sinprivilegios,\
                       generic.ListView):
    permission_required="inv.view_subcategoria"
    model = SubCategoria
    template_name = "inv/subcategoria_list.html"
    context_object_name = "obj"


class SubCategoriaNew(sinprivilegios, generic.CreateView):
    permission_required = "inv.add_subcategoria"
    model=SubCategoria
    template_name="inv/subcategoria_form.html"
    context_object_name="obj"
    form_class=SubCategoriaForm
    success_url=reverse_lazy("inv:subcategoria_list")

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)

class SubCategoriaEdit(sinprivilegios, generic.UpdateView):
    permission_required = "inv.change_subcategoria"
    model=SubCategoria
    template_name="inv/subcategoria_form.html"
    context_object_name="obj"
    form_class=SubCategoriaForm
    success_url=reverse_lazy("inv:subcategoria_list")

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)

@login_required(login_url='/login/')
@permission_required('inv.change_subcategoria', login_url='index:sin_privilegios')
def subcategoria_inactivar(request, id):
    subi = SubCategoria.objects.filter(pk=id).first()
    contexto={}
    template_name="inv/catalogos_del.html"


    if not subi:
        return redirect("inv:subcategoria_list")
    
    if request.method=='GET':
        contexto={'obj':subi}
    
    if request.method=='POST':
        subi.estado=False
        subi.save()
        messages.success(request, 'SubCategoria Inactivada!')
        return redirect("inv:subcategoria_list")

    return render(request,template_name,contexto)
    
#class SubCategoriaDel(LoginRequiredMixin, generic.DeleteView):
    #model=SubCategoria
    #template_name='inv/catalogos_del.html'
    #context_object_name='obj'
    #success_url=reverse_lazy("inv:subcategoria_list")

class MarcaView(sinprivilegios,\
     generic.ListView):
    permission_required = "inv.view_marca"
    model = Marca
    template_name = "inv/marca_list.html"
    context_object_name = "obj"

class MarcaNew(sinprivilegios,
                   generic.CreateView):
    model=Marca
    template_name="inv/marca_form.html"
    context_object_name = 'obj'
    form_class=MarcaForm
    success_url= reverse_lazy("inv:marca_list")
    success_message="Marca Creada"
    permission_required="inv.add_marca"

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)

class MarcaEdit(sinprivilegios,
                   generic.UpdateView):
    model=Marca
    template_name="inv/marca_form.html"
    context_object_name = 'obj'
    form_class=MarcaForm
    success_url= reverse_lazy("inv:marca_list")
    success_message="Marca Editada"
    permission_required="inv.change_marca"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)


@login_required(login_url='/login/')
@permission_required('inv.change_marca', login_url='index:sin_privilegios')
def marca_inactivar(request, id):
    marca = Marca.objects.filter(pk=id).first()
    contexto={}
    template_name="inv/catalogos_del.html"


    if not marca:
        return redirect("inv:marca_list")
    
    if request.method=='GET':
        contexto={'obj':marca}
    
    if request.method=='POST':
        marca.estado=False
        marca.save()
        messages.success(request, 'Marca Inactivada')
        return redirect("inv:marca_list")

    return render(request,template_name,contexto)

####################################################
class UMView(sinprivilegios, generic.ListView):
    model = UnidadMedida
    template_name = "inv/um_list.html"
    context_object_name = "obj"
    permission_required="inv.view_unidadmedida"

class UMNew(sinprivilegios,
                   generic.CreateView):
    model=UnidadMedida
    template_name="inv/um_form.html"
    context_object_name = 'obj'
    form_class=UMForm
    success_url= reverse_lazy("inv:um_list")
    # success_message="Unidad Medida Creada"
    permission_required="inv.add_unidadmedida"

    def form_valid(self, form):
        form.instance.uc = self.request.user
        print(self.request.user.id)
        return super().form_valid(form)

class UMEdit(sinprivilegios,
                   generic.UpdateView):
    model=UnidadMedida
    template_name="inv/um_form.html"
    context_object_name = 'obj'
    form_class=UMForm
    success_url= reverse_lazy("inv:um_list")
    #success_message="Unidad Medida Editada"
    permission_required="inv.change_unidadmedida"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        print(self.request.user.id)
        return super().form_valid(form)

@login_required(login_url='/login/')
@permission_required('inv.change_unidadmedida', login_url='index:sin_privilegios')
def um_inactivar(request, id):
    um = UnidadMedida.objects.filter(pk=id).first()
    contexto={}
    template_name="inv/catalogos_del.html"

    if not um:
        return redirect("inv:um_list")
    
    if request.method=='GET':
        contexto={'obj':um}
    
    if request.method=='POST':
        um.estado=False
        um.save()
        return redirect("inv:um_list")

    return render(request,template_name,contexto)

class ProductoView(sinprivilegios, generic.ListView):
    model = Producto
    template_name = "inv/prducto_list.html"
    context_object_name = "obj"
    permission_required="inv.view_producto"

class ProductoNew(sinprivilegios,
                   generic.CreateView):
    model=Producto
    template_name="inv/producto_form.html"
    context_object_name = 'obj'
    form_class=ProductoForm
    success_url= reverse_lazy("inv:producto_list")
    #success_message="Producto Creado"
    permission_required="inv.add_producto"

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)
    
    #def get_context_data(self, **kwargs):
    #    context = super(ProductoNew, self).get_context_data(**kwargs)
    #    context["categorias"] = Categoria.objects.all()
    #    context["subcategorias"] = SubCategoria.objects.all()
    #    return context


class ProductoEdit(sinprivilegios,
                   generic.UpdateView):
    model=Producto
    template_name="inv/producto_form.html"
    context_object_name = 'obj'
    form_class=ProductoForm
    success_url= reverse_lazy("inv:producto_list")
    #success_message="Producto Editado"
    permission_required="inv.change_producto"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)
    
    #def get_context_data(self, **kwargs):
    #    pk = self.kwargs.get('pk')

    #    context = super(ProductoEdit, self).get_context_data(**kwargs)
    #    context["categorias"] = Categoria.objects.all()
    #    context["subcategorias"] = SubCategoria.objects.all()
    #    context["obj"] = Producto.objects.filter(pk=pk).first()

    #    return context


@login_required(login_url="/login/")
@permission_required("inv.change_producto",login_url='index:sin_privilegios')
def producto_inactivar(request, id):
    prod = Producto.objects.filter(pk=id).first()
    contexto={}
    template_name="inv/catalogos_del.html"

    if not prod:
        return redirect("inv:producto_list")
    
    if request.method=='GET':
        contexto={'obj':prod}
    
    if request.method=='POST':
        prod.estado=False
        prod.save()
        return redirect("inv:producto_list")

    return render(request,template_name,contexto)
