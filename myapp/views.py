from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.core.management import call_command
from django.core.paginator import Paginator
from .models import Pokemon, DataRun, PokemonType, City, WeatherRecord
from .forms import PokemonForm

def home(request):
    return render(request, "myapp/home.html")

def record_list(request):
    pokemon_list = Pokemon.objects.all() # queries every Pokemon from the database
    paginator = Paginator(pokemon_list, 20) # Show 20 Pokemon per page
    page_number = request.GET.get('page') # Get the page number from the query parameters, default to 1 if not provided
    page_obj = paginator.get_page(page_number) # Get the Page object for the current page; handles out-of-range and invalid page numbers gracefully
    return render(request, "myapp/record_list.html", {"page_obj": page_obj})

def record_detail(request, pk):
    pokemon = get_object_or_404(Pokemon, pk=pk) # retrieves Pokemon w/ corresponding pk or 404 error if not found
    return render(request, "myapp/record_detail.html", {"pokemon": pokemon})

def record_create(request):
    if request.method == "POST": # fill form with submitted data and validate
        form = PokemonForm(request.POST)
        if form.is_valid(): 
            pokemon = form.save(commit=False) # allows to fill form before saving to DB
            data_run, _ = DataRun.objects.get_or_create(source='csv')
            pokemon.data_run = data_run # note: DataRun tracks which batch of data the Pokemon was imported with
            pokemon.save()
            return redirect("myapp:record_detail", pk=pokemon.pk)
    else: # GET request from Add New Pokemon link, show blank form
        form = PokemonForm()
    return render(request, "myapp/record_form.html", {"form": form})

def record_update(request, pk):
    pokemon = get_object_or_404(Pokemon, pk=pk)
    if request.method == "POST":
        form = PokemonForm(request.POST, instance=pokemon)
        if form.is_valid():
            form.save()
            return redirect("myapp:record_detail", pk=pokemon.pk)
    else:
        form = PokemonForm(instance=pokemon)
    return render(request, "myapp/record_form.html", {"form": form})

def record_delete(request, pk):
    pokemon = get_object_or_404(Pokemon, pk=pk)
    if request.method == "POST":
        pokemon.delete()
        return redirect("myapp:record_list")
    return render(request, "myapp/record_confirm_delete.html", {"pokemon": pokemon})

def get_boosted_types(temperature):
    boosted = []
    if temperature >= 85:
        boosted.append('Fire')
    if temperature <= 65:
        boosted.append('Water')
    if 65 < temperature <= 80:
        boosted.append('Grass')
    if temperature >= 90:
        boosted.append('Electric')
    return boosted if boosted else ['Normal']

def weather_boost(request):
    cities = City.objects.all()
    city_boosts = []

    for city in cities:
        latest = WeatherRecord.objects.filter(city=city).first()
        if latest:
            boosted_type_names = get_boosted_types(latest.temperature)
            boosted_types = PokemonType.objects.filter(name__in=boosted_type_names)
            boosted_pokemon = Pokemon.objects.filter(
                primary_type__in=boosted_types
            ) | Pokemon.objects.filter(
                secondary_type__in=boosted_types
            )

            city_boosts.append({
                "city": city,
                "temperature": latest.temperature,
                "timestamp": latest.timestamp,
                "boosted_types": boosted_type_names,
                "pokemon": boosted_pokemon.distinct()[:10],
            })
    return render(request, "myapp/weather_boost.html", {"city_boosts": city_boosts})

# Aiden's views for API role

@staff_member_required
def fetch_page(request):
    """GET /fetch/ — shows the trigger button (staff only)."""
    return render(request, "myapp/fetch.html", {})


@staff_member_required
@require_POST
def fetch_data_view(request):
    """POST /fetch/run/ — runs the management command in-process."""
    try:
        call_command("fetch_data")
        message = "Data fetched successfully."
        success = True
    except Exception as e:
        message = f"Error during fetch: {e}"
        success = False

    return render(request, "myapp/fetch.html", {
        "message": message,
        "success": success,
    })
