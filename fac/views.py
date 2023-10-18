from django.shortcuts import render, redirect
from django.views import generic

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.contrib import messages

from index.views import sinprivilegios

from .models import Cliente, FacturaEnc, FacturaDet
from inv.models import Producto
from .forms import ClienteForm
import inv.views as inv

from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from proyectopg import settings
import os
from jinja2 import Template
from datetime import date
import xml.etree.ElementTree as ET
from xhtml2pdf import pisa
from io import BytesIO
import base64
from django.template.loader import get_template
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Image,
    PageTemplate,
    Frame,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors


class ClienteView(sinprivilegios, generic.ListView):
    model = Cliente
    template_name = "fac/cliente_list.html"
    context_object_name = "obj"
    permission_required = "cmp.view_cliente"


class VistaBaseCreate(SuccessMessageMixin, sinprivilegios, generic.CreateView):
    context_object_name = "obj"
    success_message = "Registro Agregado Satisfactoriamente"

    def form_valid(self, form):
        form.instance.uc = self.request.user
        return super().form_valid(form)


class VistaBaseEdit(SuccessMessageMixin, sinprivilegios, generic.UpdateView):
    context_object_name = "obj"
    success_message = "Registro Actualizado Satisfactoriamente"

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        return super().form_valid(form)


class ClienteNew(VistaBaseCreate):
    model = Cliente
    template_name = "fac/cliente_form.html"
    form_class = ClienteForm
    success_url = reverse_lazy("fac:cliente_list")
    permission_required = "fac.add_cliente"


class ClienteEdit(VistaBaseEdit):
    model = Cliente
    template_name = "fac/cliente_form.html"
    form_class = ClienteForm
    success_url = reverse_lazy("fac:cliente_list")
    permission_required = "fac.change_cliente"


@login_required(login_url="/login/")
@permission_required("fac.change_cliente", login_url="/login/")
def clienteInactivar(request, id):
    cliente = Cliente.objects.filter(pk=id).first()

    if request.method == "POST":
        if cliente:
            cliente.estado = not cliente.estado
            cliente.save()
            return HttpResponse("OK")
        return HttpResponse("FAIL")

    return HttpResponse("FAIL")


class FacturaView(sinprivilegios, generic.ListView):
    model = FacturaEnc
    template_name = "fac/factura_list.html"
    context_object_name = "obj"
    permission_required = "fac.view_facturaenc"


@login_required(login_url="/login/")
@permission_required("fac.change_facturaenc", login_url="bases:sin_privilegios")
def facturas(request, id=None):
    template_name = "fac/facturas.html"

    detalle = {}
    clientes = Cliente.objects.filter(estado=True)

    if request.method == "GET":
        enc = FacturaEnc.objects.filter(pk=id).first()
        if not enc:
            encabezado = {
                "id": 0,
                "fecha": datetime.today(),
                "cliente": 0,
                "sub_total": 0.00,
                "descuento": 0.00,
                "total": 0.00,
            }
            detalle = None
        else:
            encabezado = {
                "id": enc.id,
                "fecha": enc.fecha,
                "cliente": enc.cliente,
                "sub_total": enc.sub_total,
                "descuento": enc.descuento,
                "total": enc.total,
            }

        detalle = FacturaDet.objects.filter(factura=enc)
        contexto = {"enc": encabezado, "det": detalle, "clientes": clientes}
        return render(request, template_name, contexto)

    if request.method == "POST":
        cliente = request.POST.get("enc_cliente")
        fecha = request.POST.get("fecha")
        cli = Cliente.objects.get(pk=cliente)

        if not id:
            enc = FacturaEnc(cliente=cli, fecha=fecha,estado_fel = 'N')
            if enc:
                enc.save()
                id = enc.id
        else:
            enc = FacturaEnc.objects.filter(pk=id).first()
            if enc:
                enc.cliente = cli
                enc.save()

        if not id:
            messages.error(request, "No. de Factura no detectado")
            return redirect("fac:factura_list")

        codigo = request.POST.get("codigo")
        cantidad = request.POST.get("cantidad")
        precio = request.POST.get("precio")
        s_total = request.POST.get("sub_total_detalle")
        descuento = request.POST.get("descuento_detalle")
        total = request.POST.get("total_detalle")

        prod = Producto.objects.get(codigo=codigo)
      
        det = FacturaDet(
                factura=enc,
                producto=prod,
                cantidad=cantidad,
                precio=precio,
                sub_total=s_total,
                descuento=descuento,
                total=total,
        )
        
        if det:
            det.save()

        
        
        return redirect("fac:factura_edit", id=id)

    return render(request, template_name, contexto)


class ProductView(inv.ProductoView):
    template_name = "fac/buscar_product.html"


def del_detalle_factura(request, id):
    template_name = "fac/facturadet_del.html"

    det = FacturaDet.objects.get(pk=id)

    if request.method == "GET":
        context = {"det": det}

    return render(request, template_name, context)


def facturar(request):
    if request.method == "POST":
        try:
            nit = request.POST.get("nit")
            nombre = request.POST.get("nombre")
            direccion = request.POST.get("direccion")
            factura = request.POST.get("fact")
            formato = "%d-%m-%Y"
            formatoReferencia = "%Y%m%d"
            fecha = date.today().strftime(formato)
            fechaReferencia = date.today().strftime(formatoReferencia)
            fact_enc = FacturaEnc.objects.get(id=factura)
            fact_det = FacturaDet.objects.filter(factura=factura)
            path = os.path.join(settings.MEDIA_ROOT, "template.j2")

            detalle = [
                {
                    "cantidad": "{:.2f}".format(item.cantidad),
                    "descripcion": item.producto.descripcion,
                    "descuento_detalle": "{:.2f}".format(item.descuento),
                    "porDescuento": "{:.2f}".format((item.descuento/item.sub_total)*100),
                    "sub_total": "{:.2f}".format(item.sub_total),
                    "precio": "{:.2f}".format(item.precio),
                    "total": "{:.2f}".format(item.total),
                    "codigo": item.producto.codigo,
                    "ImpNeto": "{:.7f}".format((item.total / 1.12)),
                    "iva": "{:.2f}".format(((item.total / 1.12) * 0.12)),
                    "medida": item.producto.unidad_medida.id,
                    'nombreUMedida':item.producto.unidad_medida.descripcion,
                }
                for item in fact_det
            ]

            infoFactura = {
                "nit": nit,
                "nombre": nombre,
                "direccion": direccion,
                "fecha": fecha,
                "referencia": fechaReferencia + factura,
                "totalFact": "{:.2f}".format(fact_enc.total),
                "impBruto": "{:.2f}".format(fact_enc.sub_total),
                "totalImpNeto": "{:.7f}".format(fact_enc.total / 1.12),
                "totalIva": "{:.2f}".format((fact_enc.total / 1.12) * 0.12),
                "total": "{:.2f}".format(fact_enc.total),
                "descuento": "{:.2f}".format(fact_enc.descuento),
                "detalle": detalle,
            }

            with open(path, "r") as temp:
                templateFact = temp.read()
            resultTemplate = Template(templateFact)
           
            respuestaFactura = enviarFactura(resultTemplate.render(infoFactura))

            if respuestaFactura:
                try:
                    raiz = ET.fromstring(str(respuestaFactura.strip()))
                    nodo = raiz.find(".//Serie")
                    if nodo is not None:
                        numero = raiz.find(".//Preimpreso")
                        nombreFact = raiz.find(".//Nombre")
                        direccionFact = raiz.find(".//Direccion")
                        numeroAutorizacionFact = raiz.find(".//NumeroAutorizacion")

                        infoFactura.update({"serie": nodo.text})
                        infoFactura.update({"numero": numero.text})
                        infoFactura.update({"nombreFact": nombreFact.text})
                        infoFactura.update({"direccionFact": direccionFact.text})
                        infoFactura.update(
                            {"numeroAutorizacionFact": numeroAutorizacionFact.text}
                        )
                        fact_enc.direccion_factura = direccionFact.text
                        fact_enc.nit_factura = infoFactura["nit"]
                        fact_enc.nombre_factura = nombreFact.text
                        fact_enc.numero_factura = numero.text
                        fact_enc.numero_interno = infoFactura["referencia"]
                        fact_enc.serie_factura = infoFactura["serie"]
                        fact_enc.numero_autorizacion = infoFactura[
                            "numeroAutorizacionFact"
                        ]
                        fact_enc.fecha = date.today()
                        fact_enc.estado_fel = 'F'
                        fact_enc.save()

                        pdf64 = convertirPDF(infoFactura)
                        respuesta = {
                            "flag": True,
                            "Facturapdf": pdf64
                        }
                        return JsonResponse(respuesta)
                    else:
                        respuesta = {"flag": False, "mensaje": respuestaFactura}
                        return JsonResponse(respuesta)
                except Exception as ex:
                    respuesta = {"flag": False, "mensaje": str(ex)}
                    return JsonResponse(respuesta)

            else:
                respuesta = {
                    "flag": False,
                    "mensaje": "",
                }
                return JsonResponse(respuesta)
        except Exception as ex:
            respuesta = {"flag": False, "mensaje": str(ex)}
            return JsonResponse(respuesta)


def enviarFactura(xml):
    usuario = "WSFEL_81089481"
    password = "WSFEL_LVSSJVIQI"
    nit = 81089481

    session = Session()
    session.auth = HTTPBasicAuth("usr_guatefac", "usrguatefac")
    clinte = Client(
        "https://pdte.guatefacturas.com:443/webservices63/feltestSB/Guatefac?wsdl",
        transport=Transport(session=session),
    )
    respuesta = clinte.service.generaDocumento(
        usuario, password, nit, "2", "1", "1", "R", xml
    )
    return respuesta


def convertirPDF(infoFactura):
    ancho = 612
    alto = 792
    pdf = BytesIO()
    data = data_fact(infoFactura)
    contenido = contenido_pdf(infoFactura)
    path_imagen = os.path.join(settings.MEDIA_ROOT, "carne.png")

    if len(data) > 20:
        alto = ((len(data) - 3) / 3) * 115

    doc = SimpleDocTemplate(
        pdf,
        pagesize=(ancho, alto),
        title="Carniceria Los Ángeles",
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0,
    )

    estiloTabla = TableStyle(
        [
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]
    )

    tabla = Table(data)
    tabla.setStyle(estiloTabla)
    contenido.append(tabla)

    imagen = Image(path_imagen, width=80, height=80)
    contenido.append(imagen)

    frame = Frame(
        x1=1,
        y1=0,
        width=250,
        height=alto,
        leftPadding=10,
        showBoundary=0,
    )

    page_template = PageTemplate(frames=[frame])
    doc.addPageTemplates(page_template)
    doc.build(contenido)
    pdfB64 = base64.b64encode(pdf.getvalue()).decode("utf-8")
    return pdfB64


def contenido_pdf(infoFactura):
    estilo = ParagraphStyle(
        name="Estilo", alignment=1, fontName="Helvetica-Bold", fontSize=10
    )

    estilo2 = ParagraphStyle(
        name="Estilo", alignment=1, fontName="Helvetica", fontSize=9
    )
    estilo3 = ParagraphStyle(
        name="Estilo", alignment=0, fontName="Helvetica", fontSize=9, spaceBefore=8
    )

    estilo4 = ParagraphStyle(
        name="Estilo", alignment=0, fontName="Helvetica", fontSize=9
    )
    contenido = [Paragraph("Carniceria Los Ángeles", estilo)]
    contenido.append(Paragraph("Ciudad,Ciudad", estilo2))
    contenido.append(Paragraph("Nit: 15545555", estilo2))
    contenido.append(Paragraph(f"<b>Factura NO.</b> {infoFactura['numero']}", estilo3))
    contenido.append(
        Paragraph(f"<b>Referencia NO.</b> {infoFactura['referencia']}", estilo4)
    )
    contenido.append(Paragraph(f"<b>Serie NO.</b> {infoFactura['serie']}", estilo4))
    contenido.append(Paragraph(f"<b>Fecha.</b> {infoFactura['fecha']}", estilo4))
    contenido.append(Paragraph("Numero de Autorización", estilo))
    contenido.append(Paragraph(infoFactura["numeroAutorizacionFact"], estilo2))
    contenido.append(Paragraph("=" * 37, estilo))
    contenido.append(Paragraph(f"<b>NIT.</b> {infoFactura['nit']}", estilo4))
    contenido.append(Paragraph(f"<b>Nombre.</b> {infoFactura['nombreFact']}", estilo4))
    contenido.append(
        Paragraph(f"<b>Dirección.</b> {infoFactura['direccionFact']}", estilo4)
    )
    contenido.append(Paragraph("=" * 37, estilo))
    return contenido


def data_fact(infoFactura):
    estilo5 = ParagraphStyle(
        name="Estilo",
        alignment=1,
        fontName="Helvetica",
        fontSize=7,
    )

    estilo7 = ParagraphStyle(
        name="Estilo",
        alignment=1,
        fontName="Helvetica",
        fontSize=7,
    )

    estilo8 = ParagraphStyle(
        name="Estilo",
        alignment=0,
        fontName="Helvetica",
        fontSize=7,
    )

    estilo6 = ParagraphStyle(
        name="Estilo", alignment=2, fontName="Helvetica-bold", fontSize=7
    )
    data = [
        ["Detalle" + " " * 75, "Total"],
    ]

    for item in infoFactura["detalle"]:
        palabra = ""
        descripcion = f"Cod {item['codigo']} {item['descripcion']}"
        if len(descripcion) <= 30:
            data.append([f"Cod {item['codigo']} {item['descripcion']}", ""])
        else:
            for letra in descripcion:
                palabra += letra
                if len(palabra) == 34:
                    data.append([palabra, ""])
                    palabra = ""
            if len(palabra) > 0:
                data.append([palabra, ""])
        data.append([Paragraph("Cantidad X Precio - Descuento", estilo5), ""])
        resultado = f"{item['cantidad']} {item['nombreUMedida']} X {item['precio']} - {item['descuento_detalle']}"
        data.append([Paragraph(resultado, estilo5), "Q" + item["total"]])
    data.append([Paragraph("=" * 35, estilo5), "=" * 5])
    data.append([Paragraph("Total", estilo6), "Q." + infoFactura["total"]])

    data.append([Paragraph("<b>Datos del Certificador</b>", estilo7), ""])
    data.append([Paragraph("<b>Nombre :</b> GUATEFACTURAS SOCIEDAD ANONIMA", estilo7), ""])
    data.append([Paragraph("<b>Nit :</b> 5640773-4", estilo7), ""])
    return data


def info_cliente(request):
    id = request.POST.get("id")

    cliente = Cliente.objects.get(pk=id)
    info_cliente_fact = {
        "nombre": cliente.nombres + " " + cliente.apellidos,
        "nit": cliente.nit,
        "direccion": cliente.direccion,
    }
    response = {"flag": True, "infoCliente": info_cliente_fact}
    return JsonResponse(response)


def ver_factura(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        formato = "%d-%m-%Y"
        try:

            encabezado = FacturaEnc.objects.get(id = id)
            fact_det = FacturaDet.objects.filter(factura=id)
            detalle = [
                    {
                        "cantidad": "{:.2f}".format(item.cantidad),
                        "descripcion": item.producto.descripcion,
                        "descuento_detalle": "{:.2f}".format((item.descuento)),
                        "precio": "{:.2f}".format(item.precio),
                        "total": "{:.2f}".format(item.total),
                        "codigo": item.producto.codigo,
                        "ImpNeto": "{:.7f}".format((item.total / 1.12)),
                        "iva": "{:.2f}".format(((item.total / 1.12) * 0.12)),
                        "medida": item.producto.unidad_medida.id,
                        'nombreUMedida':item.producto.unidad_medida.descripcion,
                    }
                    for item in fact_det
                ]
            
            infoFactura = {
                    "nit": encabezado.nit_factura,
                    "nombreFact": encabezado.nombre_factura,
                    "direccionFact": encabezado.direccion_factura,
                    "fecha": encabezado.fecha.strftime(formato),
                    "referencia": encabezado.numero_interno,
                    "totalFact": "{:.2f}".format(encabezado.total),
                    "impBruto": "{:.2f}".format(encabezado.total),
                    "totalImpNeto": "{:.7f}".format(encabezado.total / 1.12),
                    "totalIva": "{:.2f}".format((encabezado.total / 1.12) * 0.12),
                    "total": "{:.2f}".format(encabezado.total - encabezado.descuento),
                    "descuento": "{:.2f}".format(encabezado.descuento),
                    "numero": encabezado.numero_factura,
                    "serie":encabezado.serie_factura,
                    "numeroAutorizacionFact":encabezado.numero_autorizacion,
                    "detalle": detalle,
            }
            
            pdf64 = convertirPDF(infoFactura)
            response = {"flag": True,"Facturapdf": pdf64}
            return JsonResponse(response)
        except Exception as ex:
            response = {"flag": False, "mensaje": str(ex)}
            return JsonResponse(response)

        