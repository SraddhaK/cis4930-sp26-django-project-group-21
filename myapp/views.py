from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.core.management import call_command
from django.core.paginator import Paginator
from .models import Pokemon, DataRun, PokemonType, City, WeatherRecord
from .forms import PokemonForm
import json
import os
import pandas as pd
from django.conf import settings

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

BOOST_RULES = [
    {"type": "Fire", "condition": "Above 85°F", "check": lambda t: t >= 85},
    {"type": "Water", "condition": "Below 65°F", "check": lambda t: t <= 65},
    {"type": "Grass", "condition": "Between 65°F and 80°F", "check": lambda t: 65 < t <= 80},
    {"type": "Electric", "condition": "Above 90°F", "check": lambda t: t >= 90},
    {"type": "Ice", "condition": "Below 32°F", "check": lambda t: t <= 32},
]

def get_boosted_types(temperature):
    boosted = [rule["type"] for rule in BOOST_RULES if rule["check"](temperature)]
    return boosted if boosted else ["Normal"]

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

# Aiden's views for Analytics role
def analytics(request):
 
    # --- Load Pokemon data from DB into a DataFrame ---
    qs = Pokemon.objects.select_related('primary_type').values(
        'name',
        'primary_type__name',
        'hp',
    )
    df = pd.DataFrame(list(qs))
    if not df.empty:
        print("nrenamed w type_1")
        df.rename(columns={'primary_type__name': 'type_1'}, inplace=True)
 
    # --- 2. Load CSV for generation + full stat columns ---
    #print(f"{os.path.join(settings.BASE_DIR.parent, 'data', 'raw', 'pokemon.csv')}")
    csv_path = os.path.join(settings.BASE_DIR.parent, 'data', 'raw', 'pokemon.csv')
    try:
        csv_df = pd.read_csv(csv_path)
        csv_df.columns = [c.lower() for c in csv_df.columns]
        csv_df = csv_df[['name', 'generation', 'total_points',
                          'attack', 'defense', 'sp_attack',
                          'sp_defense', 'speed', 'type_1', 'status']].copy()
        use_csv = True
    except FileNotFoundError:
        use_csv = False
        print("couldn't find file")
        csv_df = pd.DataFrame()
 
    # Research Question 1 — "Which typing has the greatest power?" using bar chart
    if use_csv:
        type_power = (
            csv_df.groupby('type_1')['total_points']
            .mean()
            .round(1)
            .sort_values(ascending=False)
        )
        bar_labels = type_power.index.tolist()
        bar_values = type_power.values.tolist()
    else:
        fallback = df.groupby('type_1')['hp'].mean().round(1).sort_values(ascending=False)
        bar_labels = fallback.index.tolist()
        bar_values = fallback.values.tolist()
 
    bar_chart_data = {'labels': bar_labels, 'values': bar_values}
 
    # Research Question 2 — "How do power levels change across generations?" using line chart
    if use_csv:
        gen_power = (
            csv_df.groupby('generation')['total_points']
            .mean()
            .round(1)
            .sort_index()
        )
        line_labels = [f'Gen {int(g)}' for g in gen_power.index.tolist()]
        line_values = gen_power.values.tolist()
    else:
        line_labels, line_values = [], []
 
    line_chart_data = {'labels': line_labels, 'values': line_values}
 
    # Research Question 3 — "Does Florida's heat give boosted types an edge?" using donut chart
    boosted_type_names = set()
    city_temp_summary  = []
 
    for city in City.objects.all():
        latest = WeatherRecord.objects.filter(city=city).first()
        if latest:
            boosted = get_boosted_types(latest.temperature)
            boosted_type_names.update(boosted)
            city_temp_summary.append({
                'city':          city.name,
                'temperature':   latest.temperature,
                'timestamp':     latest.timestamp,
                'boosted_types': boosted,
            })
 
    if use_csv and boosted_type_names:
        csv_df['is_boosted'] = csv_df['type_1'].isin(boosted_type_names)
        boost_groups = csv_df.groupby('is_boosted')['total_points'].mean().round(1)
        boosted_avg    = float(boost_groups.get(True,  0))
        nonboosted_avg = float(boost_groups.get(False, 0))
    else:
        boosted_avg, nonboosted_avg = 0, 0
 
    doughnut_chart_data = {
        'labels': ['Boosted Types', 'Non-Boosted Types'],
        'values': [boosted_avg, nonboosted_avg],
    }
 
    # --- Summary statistics table (count, mean, min, max) ---
    if use_csv:
        summary_stats = {
            'Total Points': {
                'count': int(csv_df['total_points'].count()),
                'mean':  round(float(csv_df['total_points'].mean()), 1),
                'min':   int(csv_df['total_points'].min()),
                'max':   int(csv_df['total_points'].max()),
            },
            'Attack': {
                'count': int(csv_df['attack'].count()),
                'mean':  round(float(csv_df['attack'].mean()), 1),
                'min':   int(csv_df['attack'].min()),
                'max':   int(csv_df['attack'].max()),
            },
        }
        most_common_type  = csv_df['type_1'].value_counts().idxmax()
        most_common_count = int(csv_df['type_1'].value_counts().max())
    else:
        summary_stats = {}
        most_common_type  = 'N/A'
        most_common_count = 0
 
    return render(request, 'myapp/analytics.html', {
        'bar_chart_json':      json.dumps(bar_chart_data),
        'line_chart_json':     json.dumps(line_chart_data),
        'doughnut_chart_json': json.dumps(doughnut_chart_data),
        'summary_stats':       summary_stats,
        'city_temp_summary':   city_temp_summary,
        'boosted_type_names':  sorted(boosted_type_names),
        'most_common_type':    most_common_type,
        'most_common_count':   most_common_count,
        'use_csv':             use_csv,
    })