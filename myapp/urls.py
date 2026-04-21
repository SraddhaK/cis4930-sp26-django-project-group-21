from django.urls import path
from . import views

app_name = 'myapp'

# add the necessary urls here for app to run

urlpatterns = [
    # Homepage uncomment when homepage is made
    #path('', views.home, name='home'),

    # Analytics dashboard uncomment when analytics dashboard is made
    # path('analytics/', views.analytics, name='analytics'),

    # API fetch trigger (staff only)
    path('fetch/', views.fetch_page, name='fetch'),
    path('fetch/run/', views.fetch_data_view, name='fetch_run'),
]