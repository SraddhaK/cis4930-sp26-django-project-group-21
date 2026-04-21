from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.core.management import call_command

# Create your views here.

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
