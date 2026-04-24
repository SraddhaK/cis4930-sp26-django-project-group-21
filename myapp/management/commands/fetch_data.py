from django.core.management.base import BaseCommand
from django.db import transaction
import requests
import logging
from datetime import date, timedelta, datetime

from myapp.models import City, WeatherRecord, DataRun

logger = logging.getLogger(__name__)

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

# refactored code from project 2 and applied to making API calls
CITIES = [
    {"name": "Tallahassee, FL", "latitude": 30.44, "longitude": -84.28},
    {"name": "Miami, FL", "latitude": 25.77, "longitude": -80.19},
    {"name": "Orlando, FL", "latitude": 28.54, "longitude": -81.38},
]


class Command(BaseCommand):
    help = "Fetch yesterday's hourly temperature data from the Open-Meteo archive API and save to the database."

    def handle(self, *args, **options):
        yesterday = date.today() - timedelta(days=1)

        base_params = {
            "start_date": yesterday.isoformat(),
            "end_date": yesterday.isoformat(),
            "hourly": "temperature_2m",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
        }

        # Create a DataRun to track this fetch session
        data_run = DataRun.objects.create(source="api")
        self.stdout.write(f"Created DataRun id={data_run.pk} (source=api)")

        total_saved   = 0
        total_skipped = 0

        for city_info in CITIES:
            self.stdout.write(f"Fetching data for {city_info['name']}...")

            params = {
                **base_params,
                "latitude": city_info["latitude"],
                "longitude": city_info["longitude"],
            }

            # Get or create the City record — coordinates stored once, reused on every run
            city, city_created = City.objects.get_or_create(
                name=city_info["name"],
                defaults={
                    "latitude": city_info["latitude"],
                    "longitude": city_info["longitude"],
                },
            )
            if city_created:
                self.stdout.write(f"Created new City: {city.name}")

            # Retry logic: retry once on Timeout, give up immediately on other errors
            retries_left = 2
            while retries_left > 0:
                try:
                    response = requests.get(BASE_URL, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()

                except requests.exceptions.Timeout:
                    retries_left -= 1
                    msg = f"Request timed out for {city.name}."
                    if retries_left > 0:
                        self.stdout.write(f" {msg} Retrying...")
                    else:
                        self.stderr.write(self.style.ERROR(f" {msg} No retries left, skipping."))
                        logger.error(msg)
                    continue

                except requests.exceptions.RequestException as e:
                    retries_left = 0
                    msg = f"Request error for {city.name}: {e}"
                    self.stderr.write(self.style.ERROR(f" {msg}"))
                    logger.error(msg)
                    continue

                # --- Successful response ---
                retries_left = 0

                hourly = data.get("hourly", {})
                times = hourly.get("time", [])
                temps = hourly.get("temperature_2m", [])

                if not times:
                    self.stdout.write(f" No hourly data returned for {city.name}, skipping.")
                    continue

                city_saved   = 0
                city_skipped = 0

                with transaction.atomic():
                    for i, timestamp_str in enumerate(times):
                        temp = temps[i] if i < len(temps) else None
                        if temp is None:
                            city_skipped += 1
                            continue

                        # Parse the ISO timestamp string the API returns ("2025-04-20T14:00")
                        timestamp = datetime.fromisoformat(timestamp_str)

                        _, created = WeatherRecord.objects.update_or_create(
                            city=city,
                            timestamp=timestamp,
                            defaults={
                                "temperature": temp,
                                "source": "api",
                                "data_run": data_run,
                            },
                        )

                        if created:
                            city_saved += 1
                        else:
                            city_skipped += 1

                total_saved += city_saved
                total_skipped += city_skipped
                self.stdout.write(
                    self.style.SUCCESS(
                        f" {city.name}: {city_saved} created, {city_skipped} updated/skipped."
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Total created: {total_saved} | Total updated/skipped: {total_skipped}"
            )
        )