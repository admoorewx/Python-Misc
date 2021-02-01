from django.shortcuts import render, get_object_or_404
from .models import Metar
from .forms import MetarForm, RawMetarForm
# Create your views here.
def metar_detail_view(request):
    mtr = Metar.objects.get(id=1)
    # context = {
    #     'Site': mtr.siteID,
    #     'Lat': mtr.Lat,
    #     'Lon': mtr.Lon
    # }
    context = {
        'metar': mtr
    }
    return render(request,"Metar/metar_detail.html",context)


def metar_create_view(request):
    form = MetarForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = MetarForm()

    context = {
        'form': form
    }
    return render(request,"Metar/metar_create.html",context)

# def metar_create_view(request):
#     form = RawMetarForm()
#     if request.method == "POST":
#         form = RawMetarForm(request.POST)
#     context = {
#         'form': form,
#     }
#     return render(request,"Metar/metar_create.html", context)

def dynamic_lookup_view(request,id):
    obj = get_object_or_404(Metar, id=id)
    context = {
        "metar": obj,
    }
    return render(request,"Metar/metar_detail.html", context)

def metar_list_view(request):
    queryset = Metar.objects.all()
    context = {
        "metar_list": queryset
    }
    return render(request,"Metar/metar_list.html",context)