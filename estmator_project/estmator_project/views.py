from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from est_quote.forms import QuoteCreateForm, ClientListForm, QuoteOptionsForm
from est_client.models import Client, Company
from est_client.forms import ClientCreateForm
from est_quote.models import Quote, Category, Product, ProductProperties


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context


@login_required
def quote_view(request):
    if request.method == 'POST':
        options_form = QuoteOptionsForm()
        context = {
            'categories': Category.objects.all(),
            'options_form': options_form.as_ul,
            'client': Client.objects.get(id=request.POST['client']),
            'quote_name': request.POST['name']
        }
        return render(
            request, 'quote.html', context
        )
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def menu_view(request):
    if request.method == 'GET':
        client_form = ClientCreateForm()
        quote_form = QuoteCreateForm()
        client_list_form = ClientListForm()
        context = {
            'client_form': client_form.as_p,
            'quote_form': quote_form.as_p,
            'client_list_form': client_list_form.as_p
        }
        return render(
            request, 'menu.html', context
        )
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def quote_form_view(request):
    if request.method == 'GET':
        quote_form = QuoteCreateForm()
        return HttpResponse(quote_form.as_p())
    else:
        return HttpResponseNotAllowed(['GET'])


@login_required
def quote_edit_form_view(request):
    if request.method == 'GET':
        client = Client.objects.get(id=request.GET['pk'])
        return HttpResponse(client.quotes_select_html())
    else:
        return HttpResponseNotAllowed(['GET'])


@login_required
def client_form_view(request):
    if request.method == 'GET':
        client_form = ClientCreateForm()
        return HttpResponse(client_form.as_p())
    else:
        return HttpResponseNotAllowed(['GET'])


@login_required
def client_edit_form_view(request):
    if request.method == 'GET':
        client = Client.objects.get(id=request.GET['pk'])
        client_form = ClientCreateForm(instance=client)
        return HttpResponse(client_form.as_p())
    else:
        return HttpResponseNotAllowed(['GET'])


@login_required
def client_list_form_view(request):
    if request.method == 'GET':
        client_list_form = ClientListForm()
        return HttpResponse(client_list_form.as_p())
    else:
        return HttpResponseNotAllowed(['GET'])


@login_required
def review_quote_view(request):
    context = {}
    if request.method == 'POST':
        quote = Quote()

        quote.user = request.user
        quote.client = Client.objects.get(id=request.POST['quote_client'])
        quote.name = request.POST['quote_name']
        quote.sub_total = request.POST['sub_total']
        quote.grand_total = request.POST['grand_total']
        quote.travel_time = request.POST['travel_time']

        quote.org_street_load = 'org_street_load' in request.POST
        quote.org_midrise_elev_std = 'org_midrise_elev_std' in request.POST
        quote.org_midrise_elv_frt = 'org_midrise_elv_frt' in request.POST
        quote.org_highrise = 'org_highrise' in request.POST
        quote.org_stairs = 'org_stairs' in request.POST
        quote.org_lng_psh = 'org_lng_psh' in request.POST

        quote.dest_street_load = 'dest_street_load' in request.POST
        quote.dest_midrise_elev_std = 'dest_midrise_elev_std' in request.POST
        quote.dest_midrise_elv_frt = 'dest_midrise_elv_frt' in request.POST
        quote.dest_highrise = 'dest_highrise' in request.POST
        quote.dest_stairs = 'dest_stairs' in request.POST
        quote.dest_lng_psh = 'dest_lng_psh' in request.POST

        quote.save()

        products = request.POST.getlist('product')
        counts = request.POST.getlist('product_count')

        for i, count in enumerate(counts):
            if count > 0:
                prop = ProductProperties()
                prop.quote = quote
                prop.product = Product.objects.get(id=int(products[i]))
                prop.count = int(count)
                prop.save()

                quote.productproperties_set.add(prop)

        quote.save()
        context['quote'] = quote

    return render(
        request, 'review.html', context
    )
